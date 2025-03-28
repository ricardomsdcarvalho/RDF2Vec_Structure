*Steps*

1. Ensure that uv is installed!
    [text](https://docs.astral.sh/uv/getting-started/installation/)

2. Navigate to the RDF2Vec_Structure Folder
    ''' console
    cd home/RDF2Vec_Structure Folder

3. Open a new screen with tmux and acess it
    ''' console
    tmux new -s <name>
    tmux a -t <name>

4. Inside the screen start a new uv env
    uv venv
    source .venv/bin/activate

5. Install project dependencies
    uv sync

