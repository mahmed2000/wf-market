wf-market:
	python -m nuitka tui.py
	mv tui.bin wf-market && rm tui.build -r
