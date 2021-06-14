"""
Errors in Bauhaus follow two principles:

1. Catch user errors early and anticipate common mistakes.
Do user input validation as soon as possible.
Actively keep track of common mistakes that people make, 
and either solve them by simplifying your API, 
adding targeted error messages for these mistakes, 
or having a "solutions to common issues" page in your docs.

2. Provide detailed feedback messages upon user error.
A good error message should answer: what happened, in what context? 
What did the software expect? How can the user fix it? 
They should be contextual, informative, and actionable. 
Every error message that transparently provides the user 
with the solution to their problem means one less support ticket,
multiplied by how many times users run into the same issue.

Credit: https://blog.keras.io/user-experience-design-for-apis.html

"""

class Error(Exception):
    """ Base class for exceptions in Bauhaus """
    pass

""" core.py """
class CustomConstraintOperatorOverloadError(Error):

    def __init__(self, constraint):
        self.constraint = constraint
    
    def __str__(self) -> str:
        return "You cannot add custom_constraints when \
                objects have overloaded one of the boolean operators."

class EmptyConstraintsError(Error):
    
    def __init__(self, encoding):
        self.encoding = encoding
    
    def __str__(self) -> str:
        return f"Constraints in {self.encoding} are empty. This can happen if none of the \
                decorated classes are instantiated and if no classes or methods are decorated \
                with @constraint, no direct constraint addition, and no custom constraints."

class EmptyPropositionalVariablesError(Error):

    def __init__(self, encoding):
        self.encoding = encoding

    def __str__(self) -> str:
        return f"Propositional variables in {self.encoding} are empty. \
                This can happen if decorated classes are not instantiated."

class GroupbyOnMethodError(Error):

    def __init__(self, method_name, class_name):
        self.method_name = method_name
        self.class_name = class_name

    def __str__(self) -> str:
        return f"You can only use groupby on a class and not a method, \
                as you have tried on {self.method_name}. \
                Try using groupby on the {self.class_name} class instead."

class GroupbyWithIncorrectTypeError(Error):

    def __init__(self, parameter, value_type, class_name):
        self.parameter = parameter
        self.value_type = value_type
        self.class_name = class_name

    def __str__(self) -> str:
        return f"The provided groupby value, {self.parameter}, \
                is of type {self.value_type}. To use groupby, \
                a function or object attribute of type string must be provided \
                to partition the {self.class_name} objects."

class EncodingObjectError(Error):
    pass

class ConstraintCreationError(Error):
    
    def __init__(self, constraint, args, left, right):
        self.constraint = constraint
        self.args = args
        self.left = left
        self.right = right
    
    def __str__(self) -> str:
        return f"Some or more of your provided arguments for the {self.constraint} \
                constraint were empty or invalid. Your provided arguments were: \
                args: {self.args}, \
                left: {self.left}, right: {self.right}"

class InvalidAtMostKConstraint(Error):
    pass

class ImplicationConstraintCreationError(Error):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        message = "You are trying to create an implies all \
            constraint without providing either the \
            left or right sides of the implication.\n"
        return message + f'Your left: {self.left} and right: {self.right}'

""" constraint_builder.py """

class ImplicationConstraintRightConditionBuildError(Error):
    
    def __init__(self, constraint_builder):
        self.constraint_builder = constraint_builder

    def __str__(self) -> str:
        return f"The '{self}' cannot be built as it is decorating a class and \
                the right implication variables are not provided. \
                If it is decorating a method, ensure that the method's return is \
                valid for bauhaus or for the nnf library. Check your decorator signature and set \
                the 'right' keyword argument to such a value."

class EmptyPropositionalVariablesFromDecorationError(Error):

    def __init__(self, constraint_builder) -> None:
        self.constraint_builder = constraint_builder
    
    def __str__(self) -> str:
        return f"In the process of retrieving propositional variables \
                to build the constraint {self}, we found none. Since this \
                constraint is created from a decorator, check that you have \
                instantiated the decorated class {self._func}. Before compiling \
                the theory, you can check the propositional variables are created \
                after instantiation via: \
                -- \
                print(encoding.propositions) \
                -- \
                "

class EmptyInputsError(Error):

    def __init__(self, constraint_builder) -> None:
        self.constraint_builder = constraint_builder
    
    def __str__(self) -> str:
        return f"The propositional variables are empty for {self.constraint_builder}"

class InvalidConstraintSizeK(Error):
    
    def __init__(self, constraint_builder, k, inputs_length) -> None:
        self.constraint_builder = constraint_builder
        self.k = k
        self.inputs_length = inputs_length
    
    def __str__(self) -> str:
        return f"The provided k={self.k} is greater than the number of propositional \
                variables (i.e. {self.inputs_length} variables) for {self.constraint_builder}."

class ConstraintBuildError(Error):
    
    def __init__(self, msg) -> None:
        self.msg = msg
    
    def __str__(self) -> str:
        return self.msg

class EmptyUnderlyingConstraintError(Error):
    """ Specifically for the Exactly One constraint """
    
    def __init__(self, at_most_one, at_least_one, inputs) -> None:
        self.at_most_one = at_most_one
        self.at_least_one = at_least_one
        self.inputs = inputs
    
    def __str__(self) -> str:
        return f"The exactly one constraint is built by wrapping \
                a logical 'nnf.And' around the AtMostOne and AtLeastOne \
                constraints. One or both of these constraints are empty, therefore \
                building this constraint resulted in an error. \
                -- \
                AtMostOne: {self.at_most_one} \
                AtLeastOne: {self.at_least_one} \
                Propositional Variables: {self.inputs} \
                --"

######### utils.py #########

class ConversionToNNFVariableError(Error):

    def __init__(self, input, e) -> None:
        self.input = input
        self.e = e

    def __str__(self) -> str:
        return f"Provided input {self.input} is not of an annotated class or method, \
                instance of such as class or method, or of type nnf.Var. \
                Attempted conversion of {self.input} to nnf.Var also failed and \
                yielded the following error message: {self.e}"