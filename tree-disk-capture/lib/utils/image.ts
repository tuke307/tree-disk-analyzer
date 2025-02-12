export function completeBase64Data(base64: string, uri: string): string {
  // If the base64 string already starts with the data URI scheme, return it as-is.
  if (base64.startsWith("data:image/")) {
      return base64;
  }

  // Extract the file extension from the URI.
  const extensionMatch = uri.match(/\.([a-zA-Z0-9]+)$/);
  let extension = "jpeg"; // default extension

  if (extensionMatch && extensionMatch[1]) {
      extension = extensionMatch[1].toLowerCase();
      if (extension === "jpg") {
          // Normalize jpg to jpeg.
          extension = "jpeg";
      }
  }

  // Construct and return the complete base64 data URL.
  return `data:image/${extension};base64,${base64}`;
}