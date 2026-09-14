# Z10 Pro 外接硬盘加密保险库

最后验证：2026-09-14

## 设计与位置

外接硬盘通过匿名 Samba 共享，文件系统权限不能保护其中的明文。因此保险库采用 `age` 公钥加密：

- 密文目录：`1ABE6CDDBE6CB345/SecureVault`
- Samba 路径：`\\192.168.3.115\Share\1ABE6CDDBE6CB345\SecureVault`
- 加密私钥：rasp2 的 `~/.config/z10pro-vault/identity.txt`
- 加密公钥：rasp2 的 `~/.config/z10pro-vault/recipient.txt`
- 操作脚本：仓库中的 `scripts/z10pro-vault.sh`

只有 `.age` 密文可以放入 `SecureVault`。SSH 私钥、密码、令牌、恢复码等明文不能直接复制到该目录。Samba 用户可以看到文件名和大小，但没有 age 私钥就无法解密内容。

## 安全边界

age 私钥只保存在 rasp2，权限为 `600`，不会提交到 Git，也不会复制到 Z10 Pro 或匿名 Samba 共享。外接硬盘损坏与 rasp2 丢失是两个独立风险：必须把 age 私钥另行备份到可信的离线加密介质。

私钥路径：

```text
/home/guosq/.config/z10pro-vault/identity.txt
```

私钥一旦丢失，现有密文无法恢复。不要通过聊天、邮件或 Git 发送私钥，也不要把私钥备份到同一个 `SecureVault`。

文件名不会被加密。别在别名里写账号、网站、姓名或密码等敏感信息，推荐使用中性编号，例如 `credential-01`。

## 使用方法

进入仓库：

```bash
cd /home/guosq/workspace/raspclaw-workspace
```

### 保存一个秘密文件

先在 rasp2 上准备只允许自己读取的源文件：

```bash
chmod 600 /path/to/secret.txt
./scripts/z10pro-vault.sh put /path/to/secret.txt credential-01
```

脚本会先在 rasp2 上加密，再将密文上传到外接硬盘。远端文件名类似：

```text
credential-01-20260914-003000.age
```

每次保存都会生成带时间戳的新版本，不覆盖旧密文。确认密文可以恢复后，再自行安全删除原始明文。

### 查看密文列表

```bash
./scripts/z10pro-vault.sh list
```

### 验证密文能够解密

验证只检查完整性，不在磁盘留下解密文件：

```bash
./scripts/z10pro-vault.sh verify credential-01-20260914-003000.age
```

### 恢复秘密文件

```bash
./scripts/z10pro-vault.sh get \
  credential-01-20260914-003000.age \
  /home/guosq/recovered-secret.txt
```

恢复文件以权限 `600` 创建。脚本拒绝覆盖已经存在的目标文件。

用完后应确认相关程序不再需要该明文，再将其安全移出在线环境。对于 SSD、闪存和写时复制文件系统，普通删除命令不保证物理数据被彻底擦除。

## 支持保存的内容

脚本可加密任意单个文件，例如：

- SSH 私钥和证书
- API Token、恢复码或环境变量文件
- 密码管理器导出文件
- TLS 证书私钥
- 加密前的配置备份

目录需要先在本地打包，再上传：

```bash
tar -czf /tmp/credential-bundle.tar.gz /path/to/directory
chmod 600 /tmp/credential-bundle.tar.gz
./scripts/z10pro-vault.sh put /tmp/credential-bundle.tar.gz bundle-01
```

打包文件本身仍是明文，验证密文后应妥善处理。

## 私钥备份与恢复演练

查看公钥不会泄露解密能力：

```bash
cat ~/.config/z10pro-vault/recipient.txt
```

备份私钥时，应复制到加密 U 盘、离线密码管理器附件或其他可信介质，并保持文件权限为 `600`。不要在终端输出私钥内容。

至少做一次恢复演练：

1. 使用无敏感信息的小测试文件执行 `put`。
2. 使用 `verify` 检查密文。
3. 使用 `get` 恢复到新的临时路径。
4. 用 `cmp` 比较原文件和恢复文件。
5. 清理测试明文和测试密文。

## 故障排查

确认 Samba 可达：

```bash
smbclient -N -L //192.168.3.115
```

确认私钥权限：

```bash
stat -c '%a %n' ~/.config/z10pro-vault/identity.txt
```

期望权限为 `600`。

如果出现 `Cannot read identity file`，不要生成新私钥覆盖原文件。应从离线备份恢复原来的 `identity.txt`；新密钥不能解密旧数据。

## 配置验证记录

2026-09-14 已完成：

- 在外接硬盘创建 `SecureVault`。
- 在 rasp2 安装 age 1.2.1。
- 生成独立 age 身份，私钥权限为 `600`。
- 验证脚本不包含私钥或其他凭据。
- 使用测试文件完成加密、上传、下载、解密和内容比对后清理测试数据。
