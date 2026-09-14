#!/usr/bin/env bash

set -euo pipefail

vault_share="${Z10PRO_VAULT_SHARE:-//192.168.3.115/Share}"
vault_dir="${Z10PRO_VAULT_DIR:-1ABE6CDDBE6CB345/SecureVault}"
identity_file="${Z10PRO_VAULT_IDENTITY:-$HOME/.config/z10pro-vault/identity.txt}"
recipient_file="${Z10PRO_VAULT_RECIPIENT:-$HOME/.config/z10pro-vault/recipient.txt}"

usage() {
  cat <<'EOF'
Usage:
  z10pro-vault.sh list
  z10pro-vault.sh put SOURCE ALIAS
  z10pro-vault.sh get ENCRYPTED_NAME DESTINATION
  z10pro-vault.sh verify ENCRYPTED_NAME

ALIAS and ENCRYPTED_NAME may contain only letters, numbers, dot, underscore,
and hyphen. Each put creates a timestamped .age file and never overwrites an
existing version.
EOF
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

validate_name() {
  case "$1" in
    ""|*[!A-Za-z0-9._-]*)
      echo "Invalid name: use only letters, numbers, dot, underscore, and hyphen" >&2
      exit 1
      ;;
  esac
}

require_command age
require_command smbclient

command="${1:-}"
case "$command" in
  list)
    smbclient -N "$vault_share" -D "$vault_dir" -c 'ls'
    ;;

  put)
    source_file="${2:-}"
    alias_name="${3:-}"
    [ -f "$source_file" ] || {
      echo "Source must be a readable regular file: $source_file" >&2
      exit 1
    }
    validate_name "$alias_name"
    [ -r "$recipient_file" ] || {
      echo "Cannot read recipient file: $recipient_file" >&2
      exit 1
    }

    timestamp="$(date +%Y%m%d-%H%M%S)"
    encrypted_name="${alias_name}-${timestamp}.age"
    temporary_dir="$(mktemp -d)"
    trap 'rm -rf -- "$temporary_dir"' EXIT
    age -R "$recipient_file" -o "$temporary_dir/$encrypted_name" "$source_file"
    smbclient -N "$vault_share" -D "$vault_dir" \
      -c "put $temporary_dir/$encrypted_name $encrypted_name"
    echo "$encrypted_name"
    ;;

  get)
    encrypted_name="${2:-}"
    destination="${3:-}"
    validate_name "$encrypted_name"
    [ -n "$destination" ] || {
      echo "Destination is required" >&2
      exit 1
    }
    [ ! -e "$destination" ] || {
      echo "Refusing to overwrite: $destination" >&2
      exit 1
    }
    [ -r "$identity_file" ] || {
      echo "Cannot read identity file: $identity_file" >&2
      exit 1
    }

    temporary_dir="$(mktemp -d)"
    trap 'rm -rf -- "$temporary_dir"' EXIT
    smbclient -N "$vault_share" -D "$vault_dir" \
      -c "get $encrypted_name $temporary_dir/$encrypted_name"
    umask 077
    age -d -i "$identity_file" -o "$destination" \
      "$temporary_dir/$encrypted_name"
    echo "$destination"
    ;;

  verify)
    encrypted_name="${2:-}"
    validate_name "$encrypted_name"
    [ -r "$identity_file" ] || {
      echo "Cannot read identity file: $identity_file" >&2
      exit 1
    }

    temporary_dir="$(mktemp -d)"
    trap 'rm -rf -- "$temporary_dir"' EXIT
    smbclient -N "$vault_share" -D "$vault_dir" \
      -c "get $encrypted_name $temporary_dir/$encrypted_name"
    age -d -i "$identity_file" "$temporary_dir/$encrypted_name" >/dev/null
    echo "verified: $encrypted_name"
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
