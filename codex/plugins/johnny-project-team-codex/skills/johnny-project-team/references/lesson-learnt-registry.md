# Lesson learnt registry

Record a lesson through one atomic command:

```text
python scripts/johnny_lesson_record.py
  --project <repo>
  --role <role>
  --issue "<observed problem>"
  --cause "<verified cause>"
  --prevention "<specific prevention>"
```

The command validates required fields, writes one content-addressed JSON entry
under `.agents/lessons_learned/entries/`, and appends history. Do not separate
validation from writing and do not use legacy lock/count files.

Use the `lesson-maintainer` skill to identify duplicates, archive stale
non-critical entries, and regenerate the digest. Its scripts are explicit
maintenance commands, not hooks and not DQA evidence.
