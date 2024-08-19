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
- **Type literal:**
  - Used to pass around types as values.
  - Syntax: `<_type>`.
  - Examples: `<string>`, `<string | null | 0>`.

## Identifiers

Identifiers must start with a letter or underscore but can otherwise contain any alphanumeric or underscore characters.

Various symbols may be used to attach metadata to an identifier.
These symbols are integral parts of the identifier itself and must always be used, not just at declaration.

- Instance variable identifiers inside a class may be made private using a `#` prefix.
- Variable or function identifiers must end with a `?` if it is allowed to be null.
- Function identifiers must end with a `!` if the function body contains any [`panic` statements](#error-handling).

The order of the symbols at the start or end does not matter (i.e., `funcName!?` and `funcName?!` are interchangeable).

## Expressions

The following are valid expressions in Nouva:

- Any [literal](#Literals).
  - Examples: `true`, `0x4`.
- An identifier (name of a [variable or value](#Variables)).
- A function invocation.
  - Syntax: `_functionIdentifier(_args)` `_functionIdentifier(_args)!_errorHandlingFunction`.
  - Allows any number of comma-separated arguments.
  - Must take an error handling function if the function contains a [`panic` statement](#error-handling).
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

Variables are non-nullable by default. To mark a variable as nullable, add the `?` character to the end of the identifier.

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
  - Operators: `=`, `+=`, `-=`, `*=`, `/=`, `&=`, `|=`, `><=`, `<<=`, `>>=`, `&&=`, `||=`.
  - Examples: `x += 2`, `y /= 10`.
- **Unary reassignment**:
  - Operators: `=!=` (invert boolean and save back into variable).
  - Syntax: `_variable =!=`.
  - Example: `var x = true; x =!=; // x is now false`.

## Functions

Functions may be declared as both a block (*named*) or as an expression (*anonymous*).
Named functions are of the form `function _name(_parameters) {}` while anonymous functions drop the `_name` part.
Each parameter must have an associated [type](#types); the return type of the function is assumed.

If the function body is only one line, then it may instead be declared as a *lambda*, which uses an arrow (`=>`) instead of the curly brace syntax.

**Named function block**:
```swift
func addSquares(a: number, b: number) {
    val square_a = a * a;
    val square_b = b * b;
    return square_a + square_b;
}
```

**Anonymous function expression**:
```swift
val anonymousFunc = func (a: number, b: number) {
    return a * 2 + b * 2;
}
```

**Lambda expression**:
```swift
val lambda = func (a: number, b: number) => a ^ 2 + b ^ 2;
```

## Classes

Classes may be created with constructors and methods.
Members are public by default; use `#` to make an identifier private.

```swift
class Foo {
  // private instance variable:
  var #x = 0;
  // private nullable instance variable:
  var #y?;
  // constructor:
  (num) {
    #y? = #x;
    #x = num;
  }
  // method:
  func getValue() {
    #y? = null;
    return #x;
  }
}
```

## Types

Variables are assigned whatever type they are given on initialisation.
Multiple types may be specified, separated by pipes (`|`).
The type of a variable cannot be changed after it is initialised.

```ts
var str = "string!";
// str must be 'string' only
var numOrStr: string | number = "12";
// numOrStr may be string or a number
numOrStr = number: parseInt(numOrStr); // allowed
```

A type may be either a fundamental type (`string`, etc); a class name; or a string template tag.
A string template tag takes the format `` `contents` ``, where the contents may use braces to subtitute an expression.

```java
val num = 10;
var templateType?: `hasNumber({num})`;
// templateType is optional (may be null) but when specified must be a string of the form `hasNumber(10)`
templateType? = "hasNumber(10)"; // allowed
templateType? = null; // allowed also
templateType? = "hasNumber(12)"; // not allowed: {num} is a constant term, being 10
```

Type conversion is done by placing the type name followed by a colon (`:`) before the expression.

```js
var thisIsAString?; // `?` to make it nullable
// type is not defined yet; value is null
// the variable is only given a type once it is given a value
thisIsAString? = "a string";
thisIsAString? = string: "definitely a string"; // if you want to be explicit
// the variable is now a string
// must always now be a string type
thisIsAString? = 12; // ERROR
thisIsAString? = "another string"; // works
```

Since types are passable as literals, generics may be made without any compiler overhead:

```swift
func genericAdd?!(T, a, b) {
  if T == <string> {
    return a + "\n" + b;
  }
  else if T == <number> {
    return a + b;
  }
  else {
    panic Error("Invalid type");
  }
}
```

## Control flow

Nouva supports `if`, `else`, `while`, `for`, and `switch` control blocks.

**If/else block**:
```js
var output = "";
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


## Error handling

Nouva has unqiue syntax for errors, using `panic` to throw an error and a function to handle it that is placed after the function invocation.

You can tell that a function invocation may throw an error as the function arguments end up surrounded with `!`.

```js
class NewError {
  message?: string;
  (msg: string) {
    message? = message?;
  }
}

// `!` symbol is a necessary part of the identifier for if the function throws an error
func numFunc!(input: number) {
  if input < 10 {
    panic NewError("Too low!");
  }
  else {
    print(input)
  }
}

func errorHandler(error: NewError) {
  print(error.message);
}

numFunc!(12)!errorHandler; // error handler not called; prints 12
numFunc!(5)!errorHandler; // error handler called; prints "Too low"
numFunc!(5)!func(e)=>print(e); // same as above
```
