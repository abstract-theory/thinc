=====
Thinc
=====

THINC stands for THINC is not C++. It is a programming language that compiles into C and C++. In more technical words, it is a syntactical variant of C and C++ that uses indentation instead of curly brackets. Practically, everything you already know about C and C++ can be applied to THINC, and those proficient with C/C++ will find it has a very low learning curve.

Two-Way Compiler
----------------
This repository contains a two-way compiler that converts code back and forth between C/C++ and THINC. The compiler also preserves code comments, and it is written in Python.

======
Syntax
======

The syntax is similar to that of Python's. It is probably best illustrated by the code examples, although a written description is as follows:

* Anything that in C and C++ that would have been placed within curly braces is instead placed within an indented code block.
* An indented block of code also placed after the following keywords: public, private, protected, case, and default.
* In the first line of code before any indented code block, a colon is placed at the end of the line.
* Aliases for classes, structures, enums, typdefs are placed in the top line of code separated from the name and each other by commas.
* Do-while loops place the "while" directly after the "do".
* Commenting style is the same as in C and C++.

========
License
========
The type of open-source license is yet to be determined. It will be something along the lines of GPL or Apache. If you're so inclined, make a pull request.

========
Examples
========

Below are snippets of C and C++ code along with the equivalent snippet of THINC code.

Hello World with a for loop
-----------------------------

THINC

.. code-block:: c++

    #include <stdio.h>

    int main():
        for (int n = 0; n < 10; n++):
            printf("Hello World!\n")
        return 0

C++

.. code-block:: c++

    #include <stdio.h>

    int main() {
        for (int n = 0; n < 10; n++) {
            printf("Hello World!\n");
        }
        return 0;
    }


Do-While Loops
-----------------------------

THINC

.. code-block:: c++

    int N = 0
    do while (N < 20):
        printf("N = %d\n", N++)
    return 0

C

.. code-block:: c++

    int N = 0;
    do {
        printf("N = %d\n", N++);
    }
    while (N < 20);
    return 0;


Classes, Access Modifiers, related aliases
------------------------------------------
THINC

.. code-block:: c++

    class Circle, dot: public Geometry:
        public:
            Circle()
            ~Circle()
            float radius
            void set_radius (float)
            float area()
            float circumference()
        private:
            void areaToRadius (float)


C++

.. code-block:: c++

    class Circle: public Geometry {
        public:
            Circle();
            ~Circle();
            float radius;
            void set_radius (float);
            float area();
            float circumference();
        private:
            void areaToRadius (float);
    } dot;


Enum, Struct, Typedef, Switch, Case, Default, related aliases
-------------------------------------------------------------
THINC

.. code-block:: c++

    enum days:
        Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday

    struct cars, trucks:
        string model
        string make
        int year
        string plates

    typedef class:
        int a

    switch(v):
        case 'a':
            break
        case 'b':
            break
        default:
            break


C

.. code-block:: c++

    enum days {
        Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
    };

    struct cars {
        string model;
        string make;
        int year;
        string plates;
    } trucks;

    typedef class {int a;};

    switch(v) {
        case 'a':
            break;
        case 'b':
            break;
        default:
            break;
    }


============
Known issues
============
Pre-processor variables
-----------------------
Currently, there is no method for handling variables that are defined by pre-processor directives. It is impossible to robustly detect such variables without pre-processing, and the THINC compiler will add semi-colons to the ends lines that are determined to be THINC code. In some cases, this will result in errors.  If anyone has a robust, simple, or not so simple solution for this, send me a message. It would be a useful addition.

Aggregate array declarations
-----------------------------
These should compile from THINC into C and C++ fine. However, this feature has not been specifically implemented, and compiling to THINC is somewhat error prone. If someone can come up with a robust method for detecting these in C/C++, I'll add it to the code.




