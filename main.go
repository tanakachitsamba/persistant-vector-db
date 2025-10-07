package main

import (
	"fmt"
	"os"
	"os/exec"
)

func main() {
	// Check if Python is installed
	_, pythonErr := exec.LookPath("python3")
	if pythonErr != nil {
		fmt.Println("Python3 is not installed or not in the system PATH.")
		fmt.Println("Please install Python3 before running this program.")
		os.Exit(1)
	}

	// Prepare the command to execute the Python script
	cmd := exec.Command(
		"python3",
		"add_documents.py",
		"[\"Tomatoes, onions, baby potatoes, cabbage, cabbage leaves\", \"jolof rice\"]",
		"[{\"topic\": \"ingredients_list\"}, {\"topic\": \"favourite_recipes\"}]",
		"[\"id1\", \"id2\"]",
	)

	// Set the working directory if needed (optional)
	// cmd.Dir = "/path/to/python_script_directory"

	// Redirect the standard output and standard error to capture the output
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Run the Python script and check for errors
	err := cmd.Run()
	if err != nil {
		fmt.Println("Error executing Python script:", err)
		if exitErr, ok := err.(*exec.ExitError); ok {
			// The command completed with a non-zero exit code
			fmt.Printf("Exit code: %d\n", exitErr.ExitCode())
		}
		os.Exit(1)
	}
}
