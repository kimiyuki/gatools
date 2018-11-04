# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -E -P -a
# http://www.sphinx-doc.org/ja/stable/man/sphinx-build.html#options
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile sphinx-apidoc

sphinx-apidoc:
	rm ./api/*.rst
	sphinx-apidoc -f -e -o ./api -M ../gatools *.py
	sphinx-apidoc -f -e -o ./api -M ../utils *.py
	rm ./api/modules.rst


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "done"
	@cp -Tr ./_build/html ../docs
	@touch ../docs/.nojekyll
