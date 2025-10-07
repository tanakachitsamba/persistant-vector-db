package main

import (
	"fmt"
	"os"
	"os/exec"
)

const (
	defaultPythonExecutable = "python3"
	defaultScriptName       = "script.py"
)

var (
	defaultItemsArg  = `["Tomatoes, onions, baby potatoes, cabbage, cabbage leaves", "jollof rice"]`
	defaultTopicsArg = `[{"topic": "ingredients_list"}, {"topic": "favourite_recipes"}]`
	defaultIDsArg    = `["id1", "id2"]`
)

func main() {
	if _, pythonErr := exec.LookPath(defaultPythonExecutable); pythonErr != nil {
		fmt.Println("Python3 is not installed or not in the system PATH.")
		fmt.Println("Please install Python3 before running this program.")
		os.Exit(1)
	}

	cmd := buildLauncherCommand(defaultPythonExecutable, defaultScriptName, []string{
		defaultItemsArg,
		defaultTopicsArg,
		defaultIDsArg,
	})

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		fmt.Println("Error executing Python script:", err)
		if exitErr, ok := err.(*exec.ExitError); ok {
			fmt.Printf("Exit code: %d\n", exitErr.ExitCode())
		}
		os.Exit(1)
	}
}
