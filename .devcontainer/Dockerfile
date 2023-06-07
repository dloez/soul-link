FROM mcr.microsoft.com/devcontainers/base:jammy

RUN mkdir /commandhistory \
    && touch /commandhistory/.bash_history /commandhistory/.zsh_history \
    && chown -R vscode:vscode /commandhistory
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && echo "$SNIPPET" >> "/home/vscode/.bashrc"
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.zsh_history" \
    && echo "$SNIPPET" >> "/home/vscode/.zshrc"
RUN chsh -s /bin/zsh vscode
