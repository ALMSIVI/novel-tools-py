# Test 1

This test novel contains volumes and introductions, including special chapters and volumes, but none have independent indices.

It does NOT discard chapter indices.

It contains duplicate and missing chapters, but no such volumes.

For analyze, this novel will use a DirectoryWriter.

## Volume 1 First Volume

This is an introduction for the first volume.

This is the second paragraph of the first volume's introduction.

### Introduction Intro

This is a special chapter.

It cannot be matched using a regular NumberedMatcher; instead, one needs a SpecialMatcher.

### Chapter 1 First Chapter

This is the first chapter.

### Chapter 2 Second Chapter

This should be the second chapter.

However, the author made a mistake and put a duplicate index. Hopefully our ChapterValidator can figure this out!

## Volume 2 Second Volume

### Chapter 3 Third Chapter

This is the third chapter.

Notice that there is no intro for the second volume.

Also notice that the chapter index does not reset after a new volume.

## Easter Egg Extra Volume

This is the introduction of the extra volume.

Like the intro chapter, one needs a SpecialMatcher.

### Chapter 4 Fourth Chapter

This should be the fourth chapter.

However, the author made a mistake and skipped the index. Hopefully our ChapterValidator can figure this out!