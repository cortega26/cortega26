# Tooltician — Branding para READMEs

Este documento centraliza el badge y tagline del ecosistema Tooltician. Consúltalo
al crear, migrar o actualizar el README de cualquier proyecto del ecosistema.

## Uso

### Badge universal (SVG centralizado por idioma)

SVGs servidos estáticamente desde `tooltician.com/public/`. Cada idioma tiene su propio
archivo SVG con el texto localizado. Para cambiar el diseño se actualizan solo los SVGs
y se refleja en todos los proyectos al desplegar.

**Español (por defecto):**

```markdown
[![Parte de Tooltician](https://img.shields.io/badge/Parte_de-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

**English:**

```markdown
[![Part of Tooltician](https://img.shields.io/badge/Part_of-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

### Badge shields.io con logo (alternativa con icono)

```markdown
[![Tooltician](https://img.shields.io/badge/Tooltician-6C47FF.svg?style=flat-square&v=2)](https://tooltician.com)
```

## Tagline por idioma

Incluye SIEMPRE un tagline itálico debajo del H1, y el mismo tagline al pie.
El tagline debe describir el proyecto en ≤12 palabras, en el idioma del README.

### Español

```markdown
*Parte del [ecosistema Tooltician](https://tooltician.com) — <descripción corta del proyecto en español>.*
```

Badge recomendado:

```markdown
[![Parte de Tooltician](https://img.shields.io/badge/Parte_de-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

### English

```markdown
*Part of the [Tooltician ecosystem](https://tooltician.com) — <short project description in English>.*
```

Badge recomendado:

```markdown
[![Part of Tooltician](https://img.shields.io/badge/Part_of-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

### Français

```markdown
*Partie de l'[écosystème Tooltician](https://tooltician.com) — <description courte en français>.*
```

Badge recomendado:

```markdown
[![Partie de Tooltician](https://img.shields.io/badge/Partie_de-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

### Português

```markdown
*Parte do [ecossistema Tooltician](https://tooltician.com) — <descrição curta em português>.*
```

Badge recomendado:

```markdown
[![Parte do Tooltician](https://img.shields.io/badge/Parte_do-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

### Deutsch

```markdown
*Teil des [Tooltician-Ökosystems](https://tooltician.com) — <kurze Beschreibung auf Deutsch>.*
```

Badge recomendado:

```markdown
[![Teil von Tooltician](https://img.shields.io/badge/Teil_von-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
```

## Estructura de README

```
# <Nombre del Proyecto>

*<Tagline en idioma del proyecto>*

[![Parte de Tooltician](https://img.shields.io/badge/Parte_de-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
[![CI](...)] ...

...

---

*<Mismo tagline al pie>*
```

## Footer canónico

Siempre es el mismo tagline del header repetido al pie del README, separado por
`---` antes del tagline. Si el README ya tiene un `Built and maintained by` u otra
línea de autoría, el tagline Tooltician va debajo, no lo reemplaza.

## Proyectos del ecosistema

Para determinar si un proyecto merece el badge, pregúntate:

- ¿Es un producto, herramienta o librería publicada (PyPI, npm, Chrome Store, SaaS)?
- ¿Está vivo (mantenimiento activo, CI, releases)?
- ¿Lo has creado o mantienes tú directamente?

Si todo es sí → lleva el badge. Si es experimental/archivado/one-off → no.
