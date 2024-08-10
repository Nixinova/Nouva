# Nouva Syntax

This is a guide to the syntax of Nouva.

## Literals

Nouva contains the following literals:

- **Null**:
  - Used when no value is present.
  - `null`
- **Boolean**:
  - `true`, `false`
- **Number**:
  - Encompasses both integer and floating-point.
  - Supports any base by affixing an underscore followed by the decimal base.
  - Examples: `190`, `3.14`, `1.011_2` ('1.011' base 2), `17_8` ('17' base 8), `4f_16` ('4F' base 16), `1.A_12` ('1.A' base 12).
- **String**:
  - Must be double quoted. Can go across multiple lines.
  - Example: `"contents"`.
- **Array**:
  - Explicit indices may be given, with successor elements continuing on from that index.
  - Examples: `["a", "b"]`, `[ 1: 1, 2, 3, ]`.
  - Access a single element using `_array[_index]` or `_array[_range]`.
- **Map**:
  - Keys may be identifiers or strings.
  - Examples: `{id: "value", id_2: "value 2"}`, `{ "string key": true }`.
  - Access elements using `_object._id` or `_object."string key"`.
  - Invoke functions using  `_object._method(_args)` or `_object."method name"(_args)`.
- **Range**:
  - Creates an iterable range.
  - Syntax: `_start.._end`, where either `_start` or `_end` (but not both) may be left out.
  - Examples: `2..4`, `-3..3`.

## Expressions

The following are valid expressions in Nouva:

- Any [literal](#Literals).
  - Examples: `true`, `0x4`.
- An identifier (name of a [variable or value](#Variables)).
- A function invocation.
  - Syntax: `_functionName(_argument1)`.
- An array getter.
  - Syntax: `array[_index]` or `array[_start::_end]`.
- An object getter.
  - Syntax: `_object._identifier` or `_object."string key"`.
- A typed expression.
  - Syntax: `_type: _expression`.
  - Example: `int: 2.5 + 1`.
- A unary expression.
  - Examples: `-12`, `+6`.
- A mathematical expression.
  - Operators: add (`+`), subtract (`-`), multiply (`*`), divide (`/`), exponent (`^`).
  - Examples: `2 + 6`, `(5 + 2 ^ 6) / 4`.
- A bitwise expression.
  - Operators: and (`&`), or (`|`), xor (`><`).
  - Examples: `0b1011 & 0b0011`, `0b10 >< 0b11`.
- A logical expression.
  - Operators: and (`&&`), or (`||`).
  - Examples: `6 == 1 || 2 == 2`, `foo && bar`.
- A comparison expression.
  - Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.
  - Example: `1 < 2`, `3 + 4 != 5`.
- An anonymous [function](#Functions) expression.
  - Syntax: `function (_arguments) { _content; }`.
- A [lambda](#Functions) expression.
  - Syntax: `@(_arguments) => _expression;`.
- A parenthetical expression.
  - An expression surrounded with `(` `)` for grouping.

## Comments

Nouva supports the standard line comments (`//`) and block comments (`/* */`).

## Variables

Variables in Nouva come in two forms: mutable (*variables*) and immutable (*values*).

- **Variable declaration:** `var _identifier : _type = _expression;`
  - Both the type and the expression are optional.
- **Value declaration:** `val _identifier : _type = _expression;`
  - Specifying the type is optional.

## Reassignment

Only variables declared with `var` may be reassigned.

```kt

val a = 1;
var b = 1;
a = 2; // ERROR
b = 3; // valid
```

Reassignments may be *binary* (having both an operator and a complement) or *unary* (having only an operator).

- **Binary reassignment**:
  - Operators: `=`, `+=`, `-=`, `*=`, `/=`, `&=`, `|=`, `#=`, `<<=`, `>>=`, `&&=`, `||=`.
  - Examples: `x += 2`, `y /= 10`.
- **Unary reassignment**:
  - Operators: `=!=` (invert boolean and save back into variable).
  - Syntax: `_variable =!=`.
  - Example: `var x = true; x =!=; // x is now false`.

## Functions

Functions may be declared as both a block (*named*) or as an expression (*anonymous*).
Named functions are of the form `function _name(_parameters) {}` while anonymous functions drop the `_name` part.

If the function body is only one line, then it may instead be declared as a *lambda*, which uses an arrow (`=>`) instead of the curly brace syntax.

**Named function block**:
```swift
func addSquares(a, b) {
    val square_a = a * a;
    val square_b = b * b;
    return square_a + square_b;
}
```

**Anonymous function expression**:
```swift
val anonymousFunc = func (a, b) {
    return a * 2 + b * 2;
}
```

**Lambda expression**:
```swift
val lambda = func (a, b) => a ^ 2 + b ^ 2;
```

## Classes

Classes may be created with constructors and methods.
Members are public by default; use `#` to make an identifier private.

```js
class Foo {
  // private instance variable:
  var #x;
  // constructor:
  (num) {
    #x = num;
  }
  // method:
  func getValue() {
    return #x;
  }
}
```

## Types

Variables are assigned whatever type they are given on initialisation.
The type of a variable cannot be changed after it is initialised.

Type conversion is done by placing the type name followed by a colon (`:`) before the expression.

```js
var thisIsAString;
// type is not defined yet
// the variable is only given a type once it is given a value
thisIsAString = "a string";
thisIsAString = string: "definitely a string"; // if you want to be explicit
// the variable is now a string
// must always now be a string type
thisIsAString = 12; // ERROR
thisIsAString = "another string"; // works
```

## Control flow

Nouva supports `if`, `else`, `while`, `for`, and `switch` control blocks.

**If/else block**:
```js
var output;
if 1 + 2 < 3 {
    output = "impossible";
}
else if true == false {
    output = "also impossible";
}
else {
    output = "your PC works!";
}
```

**While loop**:
```js
var num = 1;
while num < 100 {
    num ^= 2;
}
```

**For loop**:
```c
for i : 1..10 {
    print(i);
}
val arr = ["a", "b", "c", "d"];
for x : arr {
    print("The value is: " + x);
}
```

**Switch block:**
```c
val value = true;
switch (value) {
  case true, false -> {
    print("valid");
  }
  default -> print("invalid");
}
```

## Modules and imports

You can declare what module (package) a file falls under using the `module` keyword.

A specific file from a selected module may be imported with the `import` keyword.

```c++
module foo.barBaz;

import somethingElse.FooBar;
```
