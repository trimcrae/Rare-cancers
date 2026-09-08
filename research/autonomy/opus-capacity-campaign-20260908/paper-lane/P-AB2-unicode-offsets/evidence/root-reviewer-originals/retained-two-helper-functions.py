import ast,io,tokenize
def _docstring_nodes(tree):
    """Every string constant Python treats as a docstring — module, class, function, async."""
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None) or []
        first = body[0] if body else None
        if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            out.add(id(first.value))
    return out

def _executable_source(src, tree):
    r"""`src` with comment and docstring characters blanked to spaces, offsets preserved.

    ⛔ BLANKED RATHER THAN DELETED so that the result is the same length and the same shape as the
    input: a filename that legitimately straddles a line still reads the same, and nothing here can
    accidentally splice two unrelated code fragments into a string that names a document neither of
    them mentions.
    ⚠ A source that will not tokenize keeps its comments. An unparseable module is already dropped
    by the caller; a tokenize failure on a module that DID parse is rare enough that failing open on
    the comment half — and closed on the docstring half, which needs only the AST — is preferable to
    dropping the module's real coverage.
    """
    starts = [0]
    for line in src.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def offset(lineno, col):
        # `col_offset` is a UTF-8 byte offset; every source here is read as text, so convert.
        line_start = starts[lineno - 1]
        line = src[line_start:starts[lineno]]
        return line_start + len(line.encode("utf-8")[:col].decode("utf-8", "ignore"))

    spans = []
    docs = _docstring_nodes(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and id(node) in docs:
            if node.lineno and node.end_lineno:
                spans.append((offset(node.lineno, node.col_offset),
                              offset(node.end_lineno, node.end_col_offset)))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                spans.append((offset(tok.start[0], tok.start[1]),
                              offset(tok.end[0], tok.end[1])))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass

    chars = list(src)
    for lo, hi in spans:
        for i in range(max(0, lo), min(len(chars), hi)):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)