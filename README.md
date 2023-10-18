# PDF Mermaid Munger

This is a fairly silly bit of code that I wrote to work around a serie sof difficulties with pandoc laying out mermaid diagrams out of place, and a series of very silly "weird errors" that were driving me batty. So I wrote a hacky workaround.

_This is slapdash code_, and you'll probably be better off figuring out how to make decent tools work for you. That said, if for some reason you find yourself feeling as frustrated as I was... by all means go for it.

## Requirements

This code uses python's [pdfkit](https://pypi.org/project/pdfkit/), which in turn uses [wkhtmltopdf](https://wkhtmltopdf.org/). You will have to install it as per the instructions.

Poetry should handle the rest.

Also required a decently recent version of [nodejs](https://nodejs.org), since the code execute the mermaid client through [npx](https://www.npmjs.com/package/npx).

## Future

If any... testing and making allowance for remote images, not just ones on the filesystem.
