# Tooltician — Branding para READMEs

Este documento centraliza el badge y tagline del ecosistema Tooltician. Consúltalo
al crear, migrar o actualizar el README de cualquier proyecto del ecosistema.

## Uso

### Badge universal (servido desde tooltician.com)

Una vez desplegado en `tooltician.com/public/badge.svg`:

```markdown
[![Tooltician](https://tooltician.com/badge.svg)](https://tooltician.com)
```

**Con borde redondeado y texto blanco sobre fondo morado (#6C47FF).**
Sirve para todos los idiomas; el tagline en el README aclara la afiliación.

### Badge shields.io con logo (fallback / pre-despliegue)

```markdown
[![Tooltician](https://img.shields.io/badge/Tooltician-6C47FF.svg?style=flat-square)](https://tooltician.com)
```

## Tagline por idioma

Incluye SIEMPRE un tagline itálico debajo del H1, y el mismo tagline al pie.
El tagline debe describir el proyecto en ≤12 palabras, en el idioma del README.

### Español

```markdown
*Parte del [ecosistema Tooltician](https://tooltician.com) — <descripción corta del proyecto en español>.*
```

Badge (solo si aún no se usa `badge.svg`):

```markdown
[![Parte de Tooltician](https://img.shields.io/badge/Parte%20de-Tooltician-6C47FF.svg?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIgM2g2YTQgNCAwIDAgMSA0IDR2MTRhMiAyIDAgMCAwLTItMkg0YTIgMiAwIDAgMS0yLTJWNVoiLz48cGF0aCBkPSJNMjIgM2gtNmE0IDQgMCAwIDAtNCA0djE0YTIgMiAwIDAgMSAyLTJoNGEyIDIgMCAwIDAgMi0yVjVhMiAyIDAgMCAwLTItMloiLz48L3N2Zz4=)](https://tooltician.com)
```

### English

```markdown
*Part of the [Tooltician ecosystem](https://tooltician.com) — <short project description in English>.*
```

Badge:

```markdown
[![Part of Tooltician](https://img.shields.io/badge/Part%20of-Tooltician-6C47FF.svg?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIgM2g2YTQgNCAwIDAgMSA0IDR2MTRhMiAyIDAgMCAwLTItMkg0YTIgMiAwIDAgMS0yLTJWNVoiLz48cGF0aCBkPSJNMjIgM2gtNmE0IDQgMCAwIDAtNCA0djE0YTIgMiAwIDAgMSAyLTJoNGEyIDIgMCAwIDAgMi0yVjVhMiAyIDAgMCAwLTItMloiLz48L3N2Zz4=)](https://tooltician.com)
```

### Français

```markdown
*Partie de l'[écosystème Tooltician](https://tooltician.com) — <description courte en français>.*
```

Badge: `Partie%20de-Tooltician`

### Português

```markdown
*Parte do [ecossistema Tooltician](https://tooltician.com) — <descrição curta em português>.*
```

Badge: `Parte%20do-Tooltician`

### Deutsch

```markdown
*Teil des [Tooltician-Ökosystems](https://tooltician.com) — <kurze Beschreibung auf Deutsch>.*
```

Badge: `Teil%20von-Tooltician`

## Estructura de README

```
# <Nombre del Proyecto>

*<Tagline en idioma del proyecto>*

[![Tooltician](https://tooltician.com/badge.svg)](https://tooltician.com)
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
