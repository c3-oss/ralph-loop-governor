# Ralph Loop Feature Slicing

Slice `<feature>` into implementation lanes.

Prefer lanes that:

- have observable acceptance criteria;
- can be tested independently;
- produce reviewable commits or evidence;
- isolate risky changes such as auth, data migration, external effects, or public API shape;
- leave final integration and gates explicit.

Avoid lanes that are only file inventories or vague phases such as "finish backend" and "finish frontend".

