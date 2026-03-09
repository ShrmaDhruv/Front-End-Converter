import sys
import os

# Make sure parent directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detector import detect
from layer3 import detect_with_llm

NIGHTMARE_CODE = """
export default {
  name: 'DirtyCounter',
  data() {
    return {
      count: 0,
      label: 'clicks'
    }
  },
  methods: {
    increment() {
      this.count++
      const el = document.querySelector('#display')
      el.innerHTML = this.count + ' ' + this.label
      el.addEventListener('mouseover', () => {
        document.getElementById('tooltip').innerText = 'Total: ' + this.count
      })
    },
    reset() {
      this.count = 0
      document.querySelectorAll('.counter-display').forEach(el => {
        el.innerText = '0'
      })
    }
  },
  computed: {
    doubled() {
      return this.count * 2
    }
  }
}
"""


def run():
    print("NIGHTMARE TEST — Framework Detection Edge Case")
    print("Code characteristics:")
    print("Vue Options API   data(), methods:, computed:")
    print("Raw DOM API       querySelector, getElementById")
    print("innerHTML         vanilla JS pattern")
    print("addEventListener  vanilla JS pattern")
    print("No imports        no framework package signal")
    print("No <template>     no Vue SFC signal")
    print()

    print("  LAYER 1 RESULT (Rule-Based Only)")
    layer1_result = detect(NIGHTMARE_CODE)

    print(layer1_result.summary())
    print()
    print(f"  Raw scores    : {layer1_result.scores}")
    print(f"  Is ambiguous  : {layer1_result.is_ambiguous}")

    print()
    print("─" * 60)
    print("  FULL PIPELINE RESULT (Layer 1 + Layer 3 via Ollama)")
    print("─" * 60)
    print()
    print("  Calling qwen2.5-coder:3b... (1-3 seconds)")
    print()

    try:
        merged = detect_with_llm(NIGHTMARE_CODE, layer1_result.scores)

        print(merged.summary())

        print()
        print("  DIAGNOSIS")

        vue_score  = layer1_result.scores.get("Vue",  0)
        html_score = layer1_result.scores.get("HTML", 0)
        gap        = abs(vue_score - html_score)

        print(f"\n  Vue  score : {vue_score}")
        print(f"HTML score : {html_score}")
        print(f"Score gap  : {gap} pts")
        print()

        if layer1_result.scores["Vue"] > layer1_result.scores["HTML"]:
            print("Layer 1 Vue won  (Options API rules outscored DOM rules)")
        else:
            print("Layer 1 HTML won (DOM rules outscored Options API rules)")

        if merged.ask_user:
            print("Layer 3 was uncertain — ask_user triggered.")
            print("In the real app: show manual framework selector to user.")
        else:
            print(f"Layer 3 confidently returned: {merged.detected}")
            if merged.detected == "Vue":
                print("      Correct — this IS Vue, just written with bad DOM calls inside.")
            else:
                print(f"Debatable — the DOM calls make this genuinely ambiguous.")

    except ConnectionError as e:
        print(f"\n Ollama not running: {e}")
        print("Start it with: ollama serve")
        print()
        print("Showing Layer 1 result only:")
        print(f"Detected: {layer1_result.detected}")
        print(f"Ambiguous: {layer1_result.is_ambiguous}")
    print()
if __name__ == "__main__":
    run()
