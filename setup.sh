mkdir -p ~/.streamlit/
echo "
[server]\n
headless = true\n
enableCORS=false\n
port = $PORT\n
token = "pk.eyJ1IjoiYmFmdS1kZiIsImEiOiJja2RteTIybGUxY3Z5MnhxMzJ6eTFkOXdqIn0.3lhLCtp3isEn6j1eObbLoQ"\n
\n
" > ~/.streamlit/config.toml
