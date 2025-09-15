package Calculator;

import java.util.Scanner;

/**
 * Program Name: Calculator App
 *
 * Description:
 * This program is a simple command-line calculator that allows users
 * to perform basic arithmetic operations: addition, subtraction,
 * multiplication, and division. The user inputs two numbers and chooses
 * an operator. The program then calculates and displays the result.
 * After completing a calculation, the user is prompted to perform another
 * operation or exit the program.
 *
 * Author: Billy Wellington
 * Date: 14 September 2025
 * Language: Java
 */
public class Main {

    /** User's response for performing another operation */
    static String ans, ansAgain, operator;

    /** Operands and result of arithmetic operations */
    static double valueA, valueB, result;

    /** Scanner object to read user input */
    static Scanner scanner = new Scanner(System.in);

    /**
     * Entry point of the program. Starts the calculator workflow.
     * @param args command-line arguments (not used)
     */
    public static void main(String[] args) {
        start();
    }

    /**
     * Displays the welcome message to the user.
     */
    static void welcomeMsg() {
        System.out.println("Welcome to the Calculator App!");
    }

    /**
     * Displays the goodbye message to the user before exiting.
     */
    static void goodbyeMsg() {
        System.out.println("Thank you for using the Calculator App!");
    }

    /**
     * Prompts the user to enter two numbers and selects an operator.
     * Clears the scanner buffer after reading input.
     */
    static void getDigits() {
        System.out.print("Please enter your first digit: ");
        valueA = scanner.nextDouble();
        clearScanner();

        getOperator();

        System.out.print("Please enter your second digit: ");
        valueB = scanner.nextDouble();
        clearScanner();
    }

    /**
     * Validates the operator entered by the user.
     * @return the operator as a string ("+", "-", "*", or "/")
     */
    static String decideOperator() {
        switch (operator) {
            case "+": break;
            case "-": break;
            case "*": break;
            case "/": break;
            default:
                System.out.println("Invalid operator! Please try again.");
                getOperator();
                return operator;
        }
        return operator;
    }

    /**
     * Performs the selected arithmetic operation based on user input,
     * displays the result, and prompts the user if they want to perform
     * another operation.
     */
    static void doOperation() {
        String op = decideOperator();

        switch(op) {
            case "+": result = add(valueA, valueB); break;
            case "-": result = sub(valueA, valueB); break;
            case "*": result = mul(valueA, valueB); break;
            case "/": result = div(valueA, valueB); break;
        }

        displayResults();
        getAgainAnswer();
    }

    /**
     * Asks the user if they want to perform another operation.
     * If "yes", restarts the workflow; otherwise exits the program.
     */
    static void getAgainAnswer() {
        System.out.println("\nWould you like to do another operation? Yes or No?");
        ansAgain = scanner.next();
        if (ansAgain.equalsIgnoreCase("yes"))
            startAgain();
        else
            exit();
    }

    /**
     * Restarts the calculator workflow by prompting for new inputs
     * and performing the selected operation.
     */
    static void startAgain() {
        getDigits();
        doOperation();
    }

    /**
     * Starts the calculator workflow by displaying a welcome message,
     * getting user inputs, and performing the first operation.
     */
    static void start() {
        welcomeMsg();
        getDigits();
        doOperation();
    }

    /**
     * Exits the program after displaying a goodbye message.
     */
    static void exit() {
        goodbyeMsg();
        System.exit(0);
    }

    /**
     * Displays the result of the arithmetic operation in a formatted string.
     */
    static void displayResults() {
        System.out.printf("%.2f %s %.2f = %.2f%n", valueA, operator, valueB, result);
    }

    /**
     * Clears the scanner buffer to avoid input issues.
     */
    static void clearScanner() {
        scanner.nextLine();
    }

    /**
     * Prompts the user to select an arithmetic operator.
     */
    static void getOperator() {
        displayOper();
        operator = scanner.next();
    }

    /**
     * Displays the list of available operators to the user.
     */
    static void displayOper() {
        System.out.println("Choose operator: +, -, *, /");
    }

    /**
     * Adds two numbers.
     * @param num1 first operand
     * @param num2 second operand
     * @return sum of num1 and num2
     */
    static double add(double num1, double num2) {
        result = num1 + num2;
        return result;
    }

    /**
     * Subtracts one number from another.
     * @param num1 first operand
     * @param num2 second operand
     * @return difference (num1 - num2)
     */
    static double sub(double num1, double num2) {
        return num1 - num2;
    }

    /**
     * Divides one number by another.
     * @param num1 numerator
     * @param num2 denominator
     * @return quotient (num1 / num2)
     */
    static double div(double num1, double num2) {
        return num1 / num2;
    }

    /**
     * Multiplies two numbers.
     * @param num1 first operand
     * @param num2 second operand
     * @return product of num1 and num2
     */
    static double mul(double num1, double num2) {
        return num1 * num2;
    }
}
