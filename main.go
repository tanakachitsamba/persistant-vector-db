package main

import (
	"bytes"
	"encoding/json"
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

	documents := []string{
		"Tomatoes, onions, baby potatoes, cabbage, cabbage leaves",
		"jolof rice",
	}
	metadatas := []map[string]string{
		{"topic": "ingredients_list"},
		{"topic": "favourite_recipes"},
	}
	ids := []string{"id1", "id2"}

	documentsJSON, err := json.Marshal(documents)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to encode documents payload: %v\n", err)
		os.Exit(1)
	}

	metadatasJSON, err := json.Marshal(metadatas)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to encode metadatas payload: %v\n", err)
		os.Exit(1)
	}

	idsJSON, err := json.Marshal(ids)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to encode ids payload: %v\n", err)
		os.Exit(1)
	}

	cmd := exec.Command(
		"python3",
		"add_documents.py",
		"--documents", string(documentsJSON),
		"--metadatas", string(metadatasJSON),
		"--ids", string(idsJSON),
	)

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err = cmd.Run()

	if stdout.Len() > 0 {
		fmt.Print(stdout.String())
	}

	if err != nil {
		if stderr.Len() > 0 {
			fmt.Fprint(os.Stderr, stderr.String())
		}

		if exitErr, ok := err.(*exec.ExitError); ok {
			os.Exit(exitErr.ExitCode())
		}

		fmt.Fprintf(os.Stderr, "failed to execute python command: %v\n", err)
		os.Exit(1)
	}

	if stderr.Len() > 0 {
		fmt.Fprint(os.Stderr, stderr.String())
	}
}
