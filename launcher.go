package main

import "os/exec"

// buildLauncherCommand constructs the command used to invoke the Python script.
// pythonExecutable is the interpreter to use (e.g. "python3"), script is the
// script path, and scriptArgs contains the positional arguments passed to the
// script.
func buildLauncherCommand(pythonExecutable, script string, scriptArgs []string) *exec.Cmd {
	args := append([]string{script}, scriptArgs...)
	return exec.Command(pythonExecutable, args...)
}
