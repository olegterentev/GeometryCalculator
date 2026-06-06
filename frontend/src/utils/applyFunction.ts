import type { ActiveFunction, GeoObject } from '../types/geometry'

function hasMetric(obj: GeoObject, key: 'length' | 'area' | 'perimeter'): obj is GeoObject & Record<typeof key, number> {
  return key in obj && typeof (obj as Record<string, unknown>)[key] === 'number'
}

export function applyFunction(obj: GeoObject, fn: ActiveFunction): { ok: true; message: string } | { ok: false; message: string } {
  if (fn === 'length') {
    if (!hasMetric(obj, 'length')) {
      return { ok: false, message: `Длина не определена для ${obj.label}` }
    }
    return { ok: true, message: `Длина ${obj.label}: ${obj.length}` }
  }

  if (fn === 'area') {
    if (!hasMetric(obj, 'area')) {
      return { ok: false, message: `Площадь не определена для ${obj.label}` }
    }
    return { ok: true, message: `Площадь ${obj.label}: ${obj.area}` }
  }

  if (!hasMetric(obj, 'perimeter')) {
    return { ok: false, message: `Периметр не определён для ${obj.label}` }
  }

  return { ok: true, message: `Периметр ${obj.label}: ${obj.perimeter}` }
}
