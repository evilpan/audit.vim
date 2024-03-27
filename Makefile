install:
	# install -m 644 plugin/audit.vim ~/.vim/plugin/
	if [ ! -d ~/.vim/plugin ];then
		mkdir -p ~/.vim/plugin
	fi
	ln -sf ${PWD}/plugin/audit.vim ~/.vim/plugin/
	if [ ! -d ~/.local/bin ];then
		mkdir -p ~/.local/bin
	fi
	ln -sf ${PWD}/avim.py ~/.local/bin/
