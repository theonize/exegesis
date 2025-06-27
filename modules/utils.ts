/**
 * Convert a glob pattern using '*' to a RegExp.
 * The '*' wildcard matches any non-dot sequence in an id/ref segment.
 */
export function globToRegex(pattern: string): RegExp {
  const escaped = pattern.replace(/[-/\\^$+?.()|[\]{}]/g, "\\$&");
  const regex = "^" + escaped.replace(/\*/g, "[^.]+") + "$";
  return new RegExp(regex);
}
