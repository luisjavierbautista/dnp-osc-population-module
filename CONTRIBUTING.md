# Guía de Contribución

Gracias por tu interés en contribuir al Módulo de Población del DNP. Esta guía te ayudará a empezar.

## Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Estándares de Código](#estándares-de-código)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)

---

## Código de Conducta

Este proyecto y todos los participantes están comprometidos a mantener un ambiente respetuoso y colaborativo.

---

## Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/dnp-osc-population-module.git
cd dnp-osc-population-module

# Agrega el upstream
git remote add upstream https://github.com/original-org/dnp-osc-population-module.git
```

### 2. Crear una Rama

```bash
# Actualiza tu main
git checkout main
git pull upstream main

# Crea una rama para tu feature/fix
git checkout -b feature/nombre-descriptivo
# o
git checkout -b fix/descripcion-del-bug
```

### 3. Hacer Cambios

- Realiza tus cambios siguiendo los estándares de código
- Agrega tests si es aplicable
- Actualiza documentación si es necesario

### 4. Commit

```bash
# Agrega tus cambios
git add .

# Commit con mensaje descriptivo
git commit -m "feat: agregar endpoint para migración neta"
# o
git commit -m "fix: corregir cálculo de envejecimiento"
```

Formato de commits:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, sin cambios de código
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

### 5. Push y Pull Request

```bash
git push origin feature/nombre-descriptivo
```

Luego crea un Pull Request en GitHub.

---

## Estándares de Código

### Backend (Python)

#### Style Guide
- Seguir PEP 8
- Usar `black` para formateo
- Usar `flake8` para linting

```bash
# Formatear código
black app/

# Linting
flake8 app/

# Type checking
mypy app/
```

#### Docstrings

```python
def calculate_growth(
    territorio_id: str,
    periodo: str,
    area: str = "Total"
) -> Optional[Dict]:
    """
    Calcula crecimiento poblacional por periodo.

    Args:
        territorio_id: Código DANE del territorio
        periodo: Periodo de análisis ('hasta_2019' o 'desde_2020')
        area: Área geográfica

    Returns:
        Diccionario con métricas de crecimiento o None si no hay datos

    Raises:
        ValueError: Si el periodo no es válido
    """
    pass
```

### Frontend (TypeScript/React)

#### Style Guide
- Usar TypeScript estricto
- Componentes funcionales con hooks
- Seguir convenciones de React

```typescript
// Buenos ejemplos
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  onClick: () => void
  children: React.ReactNode
}

export function Button({ variant = 'primary', onClick, children }: ButtonProps) {
  return (
    <button
      className={cn('btn', `btn-${variant}`)}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

#### Naming Conventions
- **Componentes**: PascalCase (`PopulationPyramid`)
- **Funciones**: camelCase (`calculateGrowth`)
- **Constantes**: UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Archivos**: kebab-case o PascalCase según contenido

---

## Proceso de Pull Request

### Checklist

Antes de crear un PR, asegúrate de:

- [ ] El código sigue los estándares del proyecto
- [ ] Todos los tests pasan (`pytest` para backend, `npm test` para frontend)
- [ ] Se agregaron tests para nueva funcionalidad
- [ ] La documentación está actualizada
- [ ] El commit message es descriptivo
- [ ] No hay conflictos con la rama main

### Template de PR

```markdown
## Descripción
[Descripción clara de los cambios]

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## ¿Cómo se probó?
[Describe las pruebas realizadas]

## Checklist
- [ ] Tests pasan localmente
- [ ] Documentación actualizada
- [ ] Sin warnings de linter
```

---

## Reportar Bugs

### Antes de Reportar

1. Verifica que no exista un issue similar
2. Verifica que estás usando la última versión
3. Intenta reproducir el bug en un ambiente limpio

### Template de Bug Report

```markdown
**Descripción del bug**
[Descripción clara y concisa]

**Para Reproducir**
Pasos para reproducir:
1. Ir a '...'
2. Click en '....'
3. Ver error

**Comportamiento esperado**
[Qué esperabas que sucediera]

**Screenshots**
[Si aplica]

**Ambiente:**
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11]
- Node: [e.g. 18.0]
- Docker: [e.g. 20.10]

**Contexto adicional**
[Cualquier otra información relevante]
```

---

## Sugerir Mejoras

### Template de Feature Request

```markdown
**¿La mejora está relacionada a un problema?**
[Descripción del problema]

**Describe la solución que te gustaría**
[Descripción clara de lo que quieres que suceda]

**Alternativas consideradas**
[Otras soluciones que consideraste]

**Contexto adicional**
[Screenshots, mockups, etc.]
```

---

## Testing

### Backend Tests

```bash
cd backend

# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_population_service.py
```

### Frontend Tests

```bash
cd frontend

# Ejecutar tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Documentación

Si agregas nueva funcionalidad, actualiza:

1. **README.md**: Si afecta instalación o uso general
2. **Docstrings/Comments**: En el código
3. **API Docs**: Si agregas endpoints (se genera automáticamente)
4. **INSTALL.md**: Si cambias proceso de instalación

---

## Preguntas

Si tienes preguntas:

1. Revisa la documentación existente
2. Busca en issues cerrados
3. Abre un nuevo issue con la etiqueta "question"

---

## Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la misma licencia del proyecto.
