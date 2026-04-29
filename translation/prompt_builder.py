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
You receive a component described in a framework-agnostic IR (Intermediate
Representation) as JSON and translate it into the requested target framework.

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
  - Do not add features not present in the IR
  - Do not remove features that are present in the IR
  - Do not include comments of any kind in the translated code
  - Do not include line comments, block comments, JSX comments, HTML comments,
    template comments, docstrings, or explanatory annotations
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
  - events.click  → element.addEventListener('click', handler)
  - events.change → element.addEventListener('change', handler)
  - events.submit → form.addEventListener('submit', (e) => { e.preventDefault(); handler() })

DOM updates:
  - Update DOM manually after state changes using getElementById or querySelector
  - Set element.textContent for text, element.innerHTML sparingly

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


def build_messages(ir: IR, target_framework: str) -> list[dict]:
    """
    Build Ollama messages list for translation.

    Args:
        ir               : Validated IR instance from ir_builder
        target_framework : One of React | Vue | Angular | HTML

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

    user = (
        f"Translate this component from {ir.framework} to {target_framework}.\n\n"
        f"Component IR:\n{ir_json}\n\n"
        f"Return only the {target_framework} code."
    )

    return [
        { "role": "system", "content": system },
        { "role": "user",   "content": user   },
    ]
