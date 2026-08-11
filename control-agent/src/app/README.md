# Control Agent app modules

The console follows a vertical `src/app/<module>` layout. Each module owns its
views, local components, translations and route metadata. Shared shell and
runtime adapters stay outside a module.

Keep module imports local and keep user-visible text in the module locale files.
The console is an operations surface, not a copy of the Core web application's
business pages or CSS. New field modules must document their runtime boundary
and remain disabled until their site configuration is reviewed.
