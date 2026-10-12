// Every page names the Arcana it describes: the commit of spmzt/arcana
// the book was built from, put in by the book's workflow.
(function () {
	var commit = "@ARCANA_COMMIT@";
	var main = document.querySelector("main");
	var p;

	if (main === null)
		return;
	p = document.createElement("p");
	p.className = "built-from";
	if (commit.charAt(0) === "@")
		p.textContent = "A local build of the book.";
	else {
		p.appendChild(document.createTextNode("Describes Arcana at "));
		var a = document.createElement("a");
		a.href = "https://github.com/spmzt/arcana/commit/" + commit;
		a.textContent = commit;
		p.appendChild(a);
		p.appendChild(document.createTextNode("."));
	}
	main.appendChild(p);
})();
