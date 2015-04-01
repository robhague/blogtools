# blogtools

Various tools that I use to create and maintain my blog at [http://rob.rho.org.uk](http://rob.rho.org.uk).

## Scripts

### `post_by_mail`

I've been using this script for a long while as the main way to get posts onto my blog. It accepts posts via email, adds them into a draft installation, and replies to me asking for confirmation. Assuming everything is OK, then I reply to that message and the post is pushed to the live site.

The script takes as a single argumemt a YAML configuration file (`pyyaml` is the only external dependency - you can get it via `pip` in the usual way). This file specifies the various file paths and email addresses involved - see _example_mail.yaml for a complete example. A single standard email (RFC 2822) message should be passed in pn standard input - making this happen in your local setup is left as an exercise to the reader. The script produces no output if it runs successfully.

The message should consist of alternating text and image parts. The images are saved as separate files, and the referencing HTML is inserted into the post file (which also works for Markdown).

When a post is submitted, the post file and any images are written in to the appropriate location in the draft installation; it is assumed that something like Jekyll's watch mode will automatically take care of regenerating the site as necessary. 

### `migratearchive.py`

This is an ad-hoc script to extract my pre-2008 blog posts from the generated
HTML and output them in Jekyll format. This script is not an example
of good style, nor does it attempt to be general. It was written
quickly to do the job at hand. However, it may be useful as a source
of ideas if you're trying to do a similar one-time migration.
