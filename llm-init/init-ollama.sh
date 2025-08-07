#!/bin/bash

echo "Waiting for Ollama to start..."
sleep 20

until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Waiting for Ollama API..."
    sleep 5
done

echo "Ollama is ready!"

if curl -s http://localhost:11434/api/tags | grep -q "mistral:7b"; then
    echo "Model mistral:7b already exists"
else
    echo "Downloading mistral:7b model..."
    curl -X POST http://localhost:11434/api/pull -d '{"name": "mistral:7b"}'
    echo "Model download complete!"
fi

echo "Ollama initialization complete!"

Invoke-RestMethod -Uri "http://localhost:11434/api/show" -Method POST -ContentType "application/json" -Body '{"name": "mistral:7b"}'