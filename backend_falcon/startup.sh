echo "please wait, loading LLM and starting flask..."
python3 ./app.py &
echo "llm started"
./ngrok config add-authtoken 2VItsXchQmKmWoWwpKnlGrJ8R6o_2Z2y4KkyLLijHk67krvub
./ngrok http 80