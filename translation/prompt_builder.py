"""
translation/prompt_builder.py

Builds Ollama prompt messages for framework translation.

Takes a validated IR instance and a target framework string, and
constructs a messages list for Phi3Client.chat(). The system prompt
contains deep per-framework instructions so the model knows exactly
what syntax to produce for each target.

The IR is serialised as JSON and embedded in the user message.
The model receives structured component intent — never raw source code.

Supported target frameworks:
    React    → functional component, hooks, JSX
    Vue      → Vue 3 SFC with <script setup> and Composition API
    Angular  → TypeScript class component with decorator
    HTML     → vanilla HTML with inline script, no framework

Per-framework instructions cover:
    - File/component structure
    - State management syntax
    - Lifecycle hook mapping
    - Event binding syntax
    - Props/inputs syntax
    - Computed property syntax
    - Import requirements
"""

from ast_layer.ir_schema import IR

SUPPORTED_TARGETS = {"React", "Vue", "Angular", "HTML"}

_BASE_SYSTEM = """You are an expert frontend code translator.
You receive original source code plus a framework-agnostic IR (Intermediate
Representation) as JSON and translate it into the requested target framework.

Priority:
  - Treat the ORIGINAL SOURCE CODE as canonical and highest priority
  - Use the IR as a supporting checklist, not as the only source of truth
  - If the source code and IR conflict, follow the source code
  - Preserve rendered structure, event behavior, state updates, imports,
    props, methods, lifecycle behavior, text content, classes, and styles
  - Ignore any IR entry that is not supported by the original source code

IR field meanings:
  props      — inputs the component receives from its parent
  state      — internal mutable values (init is the initial value)
  computed   — derived values that update when their dependencies change
  lifecycle  — side effects tied to component mount/destroy/update
  methods    — functions defined on the component
  imports    — external modules the component depends on
  template   — structural hints about what the component renders
  styles     — raw CSS belonging to this component

Lifecycle hook mapping:
  onMount        → runs once after the component is inserted into the DOM
  onDestroy      → runs before the component is removed
  onBeforeMount  → runs just before insertion
  onUpdate       → runs after every reactive update
  onBeforeUpdate → runs just before a reactive update
  onCreate       → runs when the component instance is created
  onChanges      → runs when input props change

Rules that always apply:
  - Preserve all state names, method names, and prop names exactly
  - Preserve method body logic as closely as possible
  - Do not add features not present in the source code
  - Do not remove features that are present in the source code
  - Use the IR to recover structure only when the source code is ambiguous
  - Never add empty placeholder lifecycle hooks, empty placeholder methods, or
    placeholder imports
  - When translating React useState setters, convert setName(...) calls into
    the target framework's state update syntax; never copy React setter calls
    into Vue, Angular, or HTML output
  - Do not include comments of any kind in the translated code
  - Do not include line comments, block comments, JSX comments, HTML comments,
    template comments, docstrings, or explanatory annotations
  - Do not output //, /* */, {/* */}, <!-- -->, or any other comment syntax
  - Return ONLY the translated code — no explanation, no markdown fences,
    no preamble, no comments about what you changed"""


_REACT_INSTRUCTIONS = """
Target: React (functional component with hooks)

Structure rules:
  - Use a named arrow function component: const ComponentName = ({ ...props }) => { ... }
  - Export default at the bottom: export default ComponentName
  - All imports at the top including React hooks

State:
  - Each IRState entry → const [name, setName] = useState(init)
  - Import useState from 'react'

Computed:
  - Each IRComputed entry → const name = useMemo(() => expression, [deps])
  - Import useMemo from 'react'
  - If deps is empty use []

Lifecycle:
  - onMount        → useEffect(() => { body }, [])
  - onDestroy      → useEffect(() => { return () => { body } }, [])
  - onUpdate       → useEffect(() => { body })
  - onEveryRender  → useEffect(() => { body })
  - onChanges      → useEffect(() => { body }, [relevant deps])
  - Import useEffect from 'react'

Props:
  - Destructure in function signature: const App = ({ prop1, prop2 }) => {
  - Required props have no default, optional props use = defaultValue

Methods:
  - Each IRMethod → const methodName = (params) => { body }
  - Async methods → const methodName = async (params) => { body }

Events (in JSX):
  - events.click   → onClick={handler}
  - events.change  → onChange={handler}
  - events.input   → onInput={handler}
  - events.submit  → onSubmit={handler}
Template:
  - Return JSX from the component function
  - Use className instead of class
  - Self-close empty elements: <br />, <input />
  - Conditionals: {condition && <Element />} or ternary
  - Loops: {items.map((item, i) => <Element key={i} />)}

Imports to always include:
  - import React from 'react'  (if using JSX or React namespace)
  - Add specific hooks to the react import: import React, { useState, useEffect } from 'react'"""


_VUE_INSTRUCTIONS = """
Target: Vue 3 SFC with <script setup> and Composition API

Structure:
  <template>
    ...
  </template>

  <script setup>
  import { ref, computed, onMounted, ... } from 'vue'
  ...
  </script>

  <style scoped>
  ...
  </style>

State:
  - Each IRState entry → const name = ref(init)
  - Access state value as name.value in script, name in template

Computed:
  - Each IRComputed entry → const name = computed(() => expression)
  - Import computed from 'vue'

Lifecycle:
  - onMount   → onMounted(() => { body });   import onMounted from 'vue'
  - onDestroy → onUnmounted(() => { body }); import onUnmounted from 'vue'
  - onUpdate  → onUpdated(() => { body });   import onUpdated from 'vue'
  - onBeforeMount  → onBeforeMount(...)
  - onBeforeDestroy → onBeforeUnmount(...)

Props:
  - defineProps({ propName: { type: Type, required: bool, default: val } })
  - Do not import defineProps — it is a compiler macro

Methods:
  - Each IRMethod → const methodName = (params) => { body }
  - Async methods → const methodName = async (params) => { body }

Events (in template):
  - events.click  → @click="handler"
  - events.change → @change="handler"
  - events.input  → @input="handler"
  - events.submit → @submit.prevent="handler"

  - Do not import click, input, change, submit, onClick, onInput, onChange,
    or any event name from 'vue'
  - Event handlers are regular local functions referenced by template directives
  - Never output React setter calls such as setCount(...) in Vue code; update
    count.value in script or count directly in the template expression
  - Do not use watchEffect to simulate click/change/input/submit handlers
  - Every template event directive must either contain a valid inline expression
    or reference a handler function that is defined in <script setup>

Template:
  - Use v-if="condition" for conditionals
  - Use v-for="item in items" :key="item.id" for loops
  - Use :propName="value" for dynamic bindings
  - Use v-model="stateName" for two-way binding
  - Use class instead of className

Imports from 'vue' to include as needed:
  ref, reactive, computed, watch, watchEffect,
  onMounted, onUnmounted, onUpdated, onBeforeMount, onBeforeUnmount"""


_ANGULAR_INSTRUCTIONS = """
Target: Angular TypeScript class component

Structure:
  import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core'

  @Component({
    selector: 'app-component-name',
    template: `...`
  })
  export class ComponentNameComponent implements OnInit, OnDestroy {
    ...
  }

State:
  - Each IRState entry → public name: type = init  (class field)
  - Use appropriate TypeScript types: string, number, boolean, any, T[]

Computed:
  - Each IRComputed entry → get name(): type { return expression }
  - Getter syntax, no decorator needed

Lifecycle:
  - onMount   → ngOnInit(): void { body }    implement OnInit
  - onDestroy → ngOnDestroy(): void { body } implement OnDestroy
  - onUpdate  → ngDoCheck(): void { body }   implement DoCheck
  - onChanges → ngOnChanges(changes): void   implement OnChanges

Props:
  - Each IRProp → @Input() propName: type
  - Required props have no default, optional use = defaultValue
  - Import Input from '@angular/core'

Outputs:
  - EventEmitter fields → @Output() eventName = new EventEmitter<type>()
  - Import Output, EventEmitter from '@angular/core'

Methods:
  - Each IRMethod → methodName(params: types): returnType { body }
  - Async methods → async methodName(...): Promise<type> { body }

Events (in template):
  - events.click  → (click)="handler()"
  - events.change → (change)="handler($event)"
  - events.input  → (input)="handler($event)"
  - events.submit → (ngSubmit)="handler()"

Template:
  - Use *ngIf="condition" for conditionals
  - Use *ngFor="let item of items; trackBy: trackFn" for loops
  - Use [propName]="value" for property bindings
  - Use [(ngModel)]="stateName" for two-way binding
  - Use class instead of className

Implements clause:
  - Add OnInit if onMount lifecycle present
  - Add OnDestroy if onDestroy lifecycle present
  - Import all implemented interfaces from '@angular/core'"""


_HTML_INSTRUCTIONS = """
Target: Vanilla HTML with inline JavaScript — no framework

Structure:
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ComponentName</title>
    <style>
      styles here
    </style>
  </head>
  <body>
    markup here
    <script>
      logic here
    </script>
  </body>
  </html>

Safety and initialization:
  - Every id or class referenced by JavaScript must exist in the HTML markup
    before it is queried
  - If the script queries DOM elements or attaches listeners, put that setup
    inside document.addEventListener('DOMContentLoaded', () => { ... }) unless
    the script is placed after every referenced element
  - DOMContentLoaded callbacks must contain real setup or an initial render call
  - Do not leave empty containers without rendering their expected content
  - Use exactly this viewport shape: content="width=device-width, initial-scale=1.0"
  - Store queried elements in constants and check them before using them:
    const button = document.getElementById('button-id')
    if (button) { button.addEventListener('click', handler) }
  - Never call addEventListener, set textContent, set innerHTML, or access value
    on a possibly null DOM element
  - Keep selectors, markup ids/classes, and JavaScript references synchronized
  - Place listener attachment in one initialization flow, not scattered at top level

State:
  - Each IRState entry → let name = init  (at top of script block)
  - Use let for mutable state, const for constants

Computed:
  - Each IRComputed entry → a function: function getName() { return expression }
  - Call as getName() wherever the value is needed

Lifecycle:
  - onMount   → document.addEventListener('DOMContentLoaded', () => { body })
  - onDestroy → window.addEventListener('beforeunload', () => { body })
  - onUpdate  → call manually after state changes

Props:
  - No props in vanilla HTML — use data attributes or URL params
  - Convert props to configurable variables at the top of the script

Methods:
  - Each IRMethod → function methodName(params) { body }
  - Async methods → async function methodName(params) { body }

Events:
  - Prefer addEventListener over inline attributes
  - Do not use inline event attributes such as onclick, onchange, oninput, or onsubmit
  - Do not assign event handler properties such as element.onclick = handler
  - events.click  → element.addEventListener('click', handler)
  - events.change → element.addEventListener('change', handler)
  - events.submit → form.addEventListener('submit', (e) => { e.preventDefault(); handler() })

  - Attach event listeners only after DOMContentLoaded or after the element markup
  - Guard each listener target with an if (element) check

DOM updates:
  - Update DOM manually after state changes using getElementById or querySelector
  - Set element.textContent for text, element.innerHTML sparingly
  - Create initial HTML markup or call render() during DOMContentLoaded so the UI
    is visible immediately
  - Every method that changes state must update the visible DOM directly or call
    a render/update function afterward
  - If the source uses React setters such as setCount, do not create setCount in
    HTML; instead update the mutable variable and then update the DOM element

Template:
  - Use standard HTML elements
  - Use id attributes to reference elements from script
  - Use class instead of className"""


_TARGET_INSTRUCTIONS = {
    "React":   _REACT_INSTRUCTIONS,
    "Vue":     _VUE_INSTRUCTIONS,
    "Angular": _ANGULAR_INSTRUCTIONS,
    "HTML":    _HTML_INSTRUCTIONS,
}


def build_messages(
    ir: IR,
    target_framework: str,
    source_code: str | None = None,
) -> list[dict]:
    """
    Build Ollama messages list for translation.

    Args:
        ir               : Validated IR instance from ir_builder
        target_framework : One of React | Vue | Angular | HTML
        source_code      : Original source code. When provided, this is
                           the highest-priority translation input.

    Returns:
        messages list for Phi3Client.chat()

    Raises:
        ValueError if target_framework is not supported
    """
    if target_framework not in SUPPORTED_TARGETS:
        raise ValueError(
            f"Unsupported target: '{target_framework}'. "
            f"Expected one of: {', '.join(sorted(SUPPORTED_TARGETS))}"
        )

    system  = _BASE_SYSTEM + "\n" + _TARGET_INSTRUCTIONS[target_framework]
    ir_json = ir.to_json()
    source_section = ""
    if source_code and source_code.strip():
        source_section = (
            "Original source code - highest priority:\n"
            "```\n"
            f"{source_code.strip()}\n"
            "```\n\n"
        )

    user = (
        f"Translate this component from {ir.framework} to {target_framework}.\n\n"
        "Use the original source code as the source of truth. "
        "Use the IR only as a supporting extraction checklist. "
        "If they disagree, the original source code wins.\n\n"
        f"{source_section}"
        f"Component IR - supporting checklist:\n{ir_json}\n\n"
        f"Return only the {target_framework} code with zero comments."
    )

    return [
        { "role": "system", "content": system },
        { "role": "user",   "content": user   },
    ]
