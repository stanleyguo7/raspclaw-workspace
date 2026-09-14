Z10 Pro SecureVault
===================

This directory is exposed through anonymous Samba. Store encrypted .age files
only. Never place plaintext passwords, private keys, API tokens, recovery codes,
or the age identity/private key here.

Encryption and recovery are performed from rasp2 with:

  /home/guosq/workspace/raspclaw-workspace/scripts/z10pro-vault.sh

The age private identity remains on rasp2 and must be backed up separately to a
trusted offline encrypted medium. Losing that identity makes the encrypted files
unrecoverable.

See knowledge/z10pro-secure-vault.md in the raspclaw-workspace repository.
