import tkinter as tk
import string
from tkinter import messagebox
from utilities import left_chars_strip


class Calculation:
    def __init__(self, root, variable, display_var):
        self.root = root
        self.variable = variable
        self.display_var = display_var
        
        self.variable_array_var = ["0"]
        
        self.errored = False
        
        self.setup_parenthesis = []
        
        self.setup_plus = False
        self.setup_minus = False
        self.setup_multiply = False
        self.setup_divide = False
        self.setup_power = False
        self.setup_perfect = False
        self.setup_modulus = False
    
    def get_array_var(self):
        return self.display_var.get().split(" ")
    
    def check_setup_method(self):
        return (self.setup_plus | self.setup_minus | self.setup_multiply |
                self.setup_divide | self.setup_power | self.setup_perfect | self.setup_modulus)
    
    def delete(self):
        self.errored = False
        self.setup_parenthesis = []
        self.set("")
        self.variable.set("0")
        self.display_var.set("0 ")
        self.set_variable_array_var(["0"])
        self.update_scaling()
    
    def backspace(self):
        if self.errored:
            self.start_integer(0)
            self.errored = False
        try:
            if (self.setup_plus | self.setup_minus | self.setup_multiply | self.setup_divide |
                    self.setup_power | self.setup_perfect | self.setup_modulus):
                self.set("")
                return
            
            if self.variable.get()[-1] == ')':
                self.setup_parenthesis.append(True)
            elif self.variable.get()[-1] == '(':
                self.setup_parenthesis.pop(0)
            
            # self.set_variable_array_var(self.variable_array_var[:-1] + [((self.variable_array_var[-1][:-1])
            # if len(self.variable_array_var[-1]) >= 2 else "0")])
            self.set_variable_array_var(
                self.variable_array_var[:-2] if not (
                    ''.join(self.variable_array_var)[-2].isdigit() or ''.join(self.variable_array_var)[-2] in ("(", ")")
                    if len(''.join(self.variable_array_var)) >= 2 else True)
                else self.variable_array_var[:-1] + (
                    ([self.variable_array_var[-1][:-1]] if ''.join(self.variable_array_var)[-2].isdigit() or ''.join(
                        self.variable_array_var)[-2] in ("(", ")") else self.variable_array_var[:-2])
                    if len(''.join(self.variable_array_var)) >= 2 else ["0"]))
            self.variable.set(((self.variable.get()[:-1] if self.variable.get()[-2].isdigit() else
                                self.variable.get()[:-2]) if len(self.variable.get()) >= 2 else "0").lstrip())
            self.display_var.set(((self.display_var.get()[:-2] if self.display_var.get()[-3] != " " else
                                   self.display_var.get()[:-5]) + " " if len(self.display_var.get()) >= 3 else "0 ").
                                 lstrip())
            self.update_scaling()
        except Exception as e:
            print(e.__class__.__name__, e)
            self.trigger_error()
    
    def remove_dot(self):
        if self.errored:
            self.start_integer(0)
            self.errored = False
        try:
            if self.setup_parenthesis:
                self.variable.set((''.join(self.variable_array_var[:-1]) + (
                        '(' * left_chars_strip(self.variable_array_var[-1], '(')[0]) + str(int(float(
                            left_chars_strip(self.variable_array_var[-1], '(')[1]) // 1))).lstrip())
                self.display_var.set((' '.join(self.get_array_var()[:-2]) + (
                    " " if len(self.get_array_var()) != 1 else "") + ('(' * left_chars_strip(
                        self.get_array_var()[-2], '(')[0]) + str(int(float(left_chars_strip(
                            self.get_array_var()[-2], '(')[1]) // 1)) + " ").lstrip())
                self.set_variable_array_var(self.variable_array_var[:-1] + [('(' * left_chars_strip(
                        self.variable_array_var[-1], '(')[0]) + str(int(float(left_chars_strip(
                            self.variable_array_var[-1], '(')[1]) // 1))])
            else:
                self.variable.set((''.join(self.variable_array_var[:-1]) + str(int(float(
                    self.variable_array_var[-1]) // 1))).lstrip())
                self.display_var.set((' '.join(self.get_array_var()[:-2]) + (" " if len(
                    self.get_array_var()) != 1 else "") + str(int(float(
                        self.get_array_var()[-2]) // 1)) + " ").lstrip())
                self.set_variable_array_var(self.variable_array_var[:-1] + [str(int(float(
                    self.variable_array_var[-1]) // 1))])
            self.update_scaling()
        except Exception as e:
            print(e.__class__.__name__, e)
            self.trigger_error()
            
    def trigger_error(self):
        self.display_var.set("Error ")
        self.errored = True
    
    def equal(self):
        if self.errored:
            self.start_integer(0)
            self.errored = False
        try:
            letters = list(string.ascii_letters)
            letters.remove("e")
            letters.remove("E")
            if self.variable.get() in letters:
                raise SyntaxError("Cannot have letters except e")  # this is for safety, we cant have functions
            result = float(eval(self.variable.get()))
            if not result % 1:
                result = int(result)
            operation = self.variable.get()
            op_display = self.display_var.get()
            op_array = str(self.variable_array_var)
                
            self.variable.set(str(result).lstrip())
            self.display_var.set((str(result) + " ").lstrip())
            self.set_variable_array_var([str(result) + " ".lstrip()])
            if self.root.database_preferences.get_preferences("storehistory")[0][2] == '1':
                for i in operation:
                    if i in ('+', '-', '*', '/', '%', '(', ')'):
                        self.root.database_history.add_to_history(operation, op_display, op_array, self.variable.get(),
                                                                  self.display_var.get(), str(self.variable_array_var))
                        if self.root.settings_open and self.root.settings_instance.get_tab() == 'history':
                            self.root.settings_instance.switch_tab('history')
                        break
        except Exception as e:
            print(e.__class__.__name__, e)
            self.trigger_error()
        
        self.update_scaling()
        
    def action(self, integer: float | str | None):
        if isinstance(integer, float) or isinstance(integer, int):
            if not integer % 1:
                integer = int(integer)
        
        if self.errored:
            self.start_integer(integer)
            self.errored = False
        elif self.setup_plus:
            self.plus(integer)
        elif self.setup_minus:
            self.minus(integer)
        elif self.setup_multiply:
            self.multiply(integer)
        elif self.setup_divide:
            self.divide(integer)
        elif self.setup_power:
            self.power(integer)
        elif self.setup_perfect:
            self.perfect(integer)
        elif self.setup_modulus:
            self.modulus(integer)
        else:
            self.add_integer(integer)
            
        self.set("")
        
        self.update_scaling()
    
    def set_variable_array_var(self, new_list):
        self.variable_array_var = new_list
    
    def update_scaling(self):
        self.root.style.configure("CalcField.TLabel", font=(
            "Consolas", 26 if len(self.display_var.get()) < 10 else 35-len(self.display_var.get())
            if 35-len(self.display_var.get()) >= 12 else 10))
        
    def add_integer(self, integer: float | int):
        if self.variable_array_var[-1] == '0':
            self.display_var.set(f"{self.display_var.get()[:-2]}{integer} ")
            self.variable.set(f"{self.variable.get()[:-1]}{integer}")
            self.variable_array_var[-1] = f"{self.variable_array_var[-1][:-1]}{integer}"
        elif self.variable_array_var[-1:-2] == '-0':
            self.display_var.set(f"{self.display_var.get()[:-2]}{integer} ")
            self.variable.set(f"{self.variable.get()[:-1]}{integer}")
            self.variable_array_var[-1] = f"{self.variable_array_var[-1][:-1]}{integer}"
        else:
            self.display_var.set(f"{self.display_var.get()[:-1]}{integer} ")
            self.variable.set(f"{self.variable.get()}{integer}")
            self.variable_array_var[-1] = f"{self.variable_array_var[-1]}{integer}"
    
    def start_integer(self, integer: float | int):
        self.display_var.set(f"{integer} ")
        self.variable.set(f"{integer}")
        self.variable_array_var = [f"{integer}"]
    
    def dot(self):
        if self.get_array_var()[-2].find(".") == -1 and not self.check_setup_method():
            self.display_var.set(self.display_var.get()[:-1] + ". ")
            self.variable.set(self.variable.get() + ".")
            self.variable_array_var[-1] += "."
        elif self.get_array_var()[-2].find(".") == -1 and self.check_setup_method():
            self.action(0)
            self.dot()
    
    def open_paranthesis(self):
        if not self.check_setup_method() and self.variable.get()[-1] != '(':
            return
        if self.variable.get()[-1] != '(':
            self.action(None)
            self.display_var.set(self.display_var.get() + f"( ")
        else:
            self.display_var.set(self.display_var.get()[:-1] + f"( ")
        self.setup_parenthesis.append(True)
        self.variable.set(self.variable.get() + f"(")
        self.variable_array_var += ["("]
        self.set("")
        
    def close_paranthesis(self):
        if self.check_setup_method():
            return
        if not self.setup_parenthesis:
            return
        
        self.display_var.set(self.display_var.get()[:-1] + f") ")
        self.variable.set(self.variable.get() + f")")
        self.variable_array_var = self.variable_array_var[:-1] + [self.variable_array_var[-1]+")"]
        self.setup_parenthesis.pop(0)
    
    def plus(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"+ {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"+{integer if integer is not None else ''}")
        self.variable_array_var += ["+", f"{integer}"] if integer is not None else ["+"]
    
    def minus(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"- {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"-{integer if integer is not None else ''}")
        self.variable_array_var += ["-", f"{integer}"] if integer is not None else ["-"]
    
    def multiply(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"x {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"*{integer if integer is not None else ''}")
        self.variable_array_var += ["*", f"{integer}"] if integer is not None else ["*"]
    
    def divide(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"÷ {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"/{integer if integer is not None else ''}")
        self.variable_array_var += ["/", f"{integer}"] if integer is not None else ["/"]
    
    def power(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"^ {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"**{integer if integer is not None else ''}")
        self.variable_array_var += ["**", f"{integer}"] if integer is not None else ["**"]
    
    def perfect(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"// {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"//{integer if integer is not None else ''}")
        self.variable_array_var += ["//", f"{integer}"] if integer is not None else ["//"]
    
    def modulus(self, integer: float | int):
        self.display_var.set(self.display_var.get() + f"% {(str(integer)+' ') if integer is not None else ''}")
        self.variable.set(self.variable.get() + f"%{integer if integer is not None else ''}")
        self.variable_array_var += ["%", f"{integer}"] if integer is not None else ["%"]
        
    def set(self, setup_type: str):
        if setup_type == 'plus':
            self.setup_plus = True
            self.setup_minus = self.setup_multiply = self.setup_divide = self.setup_power = self.setup_perfect =\
                self.setup_modulus = False
        elif setup_type == 'minus':
            if self.display_var.get() == '0 ':
                user_input = messagebox.askyesno(message="Start as negative number?\nYes=Negative Number, No=Subtract",
                                                 title="Choose")
                
                if user_input:
                    self.display_var.set(f"- ")
                    self.variable.set(f"-")
                    self.variable_array_var = [f"-"]
                    return
            elif self.check_setup_method() or self.variable.get()[-1] == '(':
                self.action("-")
                return
            
            self.setup_minus = True
            self.setup_plus = self.setup_multiply = self.setup_divide = self.setup_power = self.setup_perfect =\
                self.setup_modulus = False
        elif setup_type == 'multiply':
            self.setup_multiply = True
            self.setup_plus = self.setup_minus = self.setup_divide = self.setup_power = self.setup_perfect =\
                self.setup_modulus = False
        elif setup_type == 'divide':
            self.setup_divide = True
            self.setup_plus = self.setup_minus = self.setup_multiply = self.setup_power = self.setup_perfect =\
                self.setup_modulus = False
        elif setup_type == 'power':
            self.setup_power = True
            self.setup_plus = self.setup_minus = self.setup_multiply = self.setup_divide = self.setup_perfect =\
                self.setup_modulus = False
        elif setup_type == 'perfect':
            self.setup_perfect = True
            self.setup_plus = self.setup_minus = self.setup_multiply = self.setup_divide = self.setup_power =\
                self.setup_modulus = False
        elif setup_type == 'modulus':
            self.setup_modulus = True
            self.setup_plus = self.setup_minus = self.setup_multiply = self.setup_divide = self.setup_power =\
                self.setup_perfect = False
        else:
            self.setup_plus = self.setup_minus = self.setup_multiply = self.setup_divide = self.setup_power =\
                self.setup_perfect = self.setup_modulus = False
            
    
    