package main

import (
	"path/filepath"
	"reflect"
	"testing"
)

func TestBuildLauncherCommand(t *testing.T) {
	scriptArgs := []string{"arg1", "arg2"}
	cmd := buildLauncherCommand("python3", "script.py", scriptArgs)

	expectedArgs := append([]string{"python3", "script.py"}, scriptArgs...)
	if !reflect.DeepEqual(cmd.Args, expectedArgs) {
		t.Fatalf("expected args %v, got %v", expectedArgs, cmd.Args)
	}

	if filepath.Base(cmd.Path) != "python3" {
		t.Fatalf("expected command path to end with python3, got %s", cmd.Path)
	}
}

func TestBuildLauncherCommandNoArgs(t *testing.T) {
	cmd := buildLauncherCommand("python3", "script.py", nil)

	expectedArgs := []string{"python3", "script.py"}
	if !reflect.DeepEqual(cmd.Args, expectedArgs) {
		t.Fatalf("expected args %v, got %v", expectedArgs, cmd.Args)
	}

	if filepath.Base(cmd.Path) != "python3" {
		t.Fatalf("expected command path to end with python3, got %s", cmd.Path)
	}
}
