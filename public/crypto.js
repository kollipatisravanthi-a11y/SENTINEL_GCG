window.SentinelCrypto = (() => {
  const encoder = new TextEncoder();

  function bytesToBase64(bytes) {
    let binary = "";
    const chunkSize = 0x8000;
    for (let i = 0; i < bytes.length; i += chunkSize) {
      const chunk = bytes.subarray(i, i + chunkSize);
      binary += String.fromCharCode(...chunk);
    }
    return btoa(binary);
  }

  function base64ToBytes(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }

  function pemToArrayBuffer(pem) {
    const body = pem
      .replace("-----BEGIN PUBLIC KEY-----", "")
      .replace("-----END PUBLIC KEY-----", "")
      .replace(/\s+/g, "");
    return base64ToBytes(body).buffer;
  }

  async function importRsaPublicKey(pem) {
    return crypto.subtle.importKey(
      "spki",
      pemToArrayBuffer(pem),
      { name: "RSA-OAEP", hash: "SHA-256" },
      false,
      ["encrypt"]
    );
  }

  async function sha256Hex(buffer) {
    const digest = await crypto.subtle.digest("SHA-256", buffer);
    return Array.from(new Uint8Array(digest))
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
  }

  async function encryptPayload(payload, publicKeyPem) {
    const plaintext = encoder.encode(JSON.stringify(payload));
    const aesKey = await crypto.subtle.generateKey(
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt"]
    );
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = new Uint8Array(
      await crypto.subtle.encrypt({ name: "AES-GCM", iv }, aesKey, plaintext)
    );
    const rawKey = await crypto.subtle.exportKey("raw", aesKey);
    const publicKey = await importRsaPublicKey(publicKeyPem);
    const encryptedKey = new Uint8Array(
      await crypto.subtle.encrypt({ name: "RSA-OAEP" }, publicKey, rawKey)
    );

    return {
      ciphertext: bytesToBase64(encrypted.slice(0, -16)),
      auth_tag: bytesToBase64(encrypted.slice(-16)),
      iv: bytesToBase64(iv),
      encrypted_key: bytesToBase64(encryptedKey),
    };
  }

  return {
    bytesToBase64,
    encryptPayload,
    sha256Hex,
  };
})();

