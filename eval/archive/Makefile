
JUP_FLAGS=--execute --ExecutePreprocessor.kernel_name=python3

.PHONY=all clean

all: analysis.html

analysis.html: analysis.ipynb
	jupyter-nbconvert $(JUP_FLAGS) --to html --template basic $^

clean:
	rm analysis.html
