# Storage: NFS, iSCSI, HAST

**Storage**, in the side bar: what a host serves of its disks to the
network, by FreeBSD's own daemons, nothing to install. Choose the host
at the top; a tab each. Each change is a task; the page reads the host
again when it ends. A host's own disks, pools and datasets are its
**Storage** tab (Devices).

## NFS

The NFS server: `nfsd(8)` with `mountd(8)` and `rpcbind(8)`, and for
NFSv4 `nfsuserd(8)`'s names.

- **Serves NFS** enables nfsd (`nfs_server_enable`, with `rpcbind` and
  `mountd`) and starts it, or stops it.
- **NFSv4**, and **NFSv4 alone** (`nfsv4_server_enable`,
  `nfsv4_server_only`: no NFSv3, mountd for the exports alone).
- **NFSv4 up to** 4.0, 4.1 or 4.2 (`vfs.nfsd.server_max_minorversion`,
  kept in `sysctl.conf`). 4.2 brings server-side copy
  (`copy_file_range(2)`), sparse files (`SEEK_HOLE`) and allocation.
- **Threads**: nfsd's (`-n`).
- **pNFS data servers**: this host the metadata server of parallel NFS
  (`pnfsserver(4)`), the data servers each an NFSv4.1 or later server
  exporting a directory to it, `ds1:/DSstore0,ds2:/DSstore1` (nfsd's
  `-p`); **Mirrors**, each file on so many of them (`-m`). Clients
  (`mount -o nfsv4,minorversion=2,pnfs`) read and write a file's data on
  the data servers directly, the metadata server telling them where.

**What it exports** is `/etc/exports` (`exports(5)`): a line a
directory and who may mount it, and for NFSv4 its root, a `V4:` line.
Saving writes it and has mountd read it again. **Exported now** is what
mountd says (`showmount -e`). A ZFS dataset may export itself instead
(`sharenfs`, its Storage tab).

`arcanactl nfs exports FILE` and `arcanactl nfs server enable=yes v4=yes
minor=2 threads=16 pnfs=ds1:/DSstore0,ds2:/DSstore1 mirror=2` do the
same.

## iSCSI

The iSCSI target: `ctld(8)` and `ctl.conf(5)`, the kernel's CAM Target
Layer serving LUNs: ZFS volumes (`/dev/zvol/pool/vol`), disks or files.
**Enable and start the target** turns ctld on (`ctld_enable`).

**A target** adds one to `ctl.conf`: its name (an IQN), its LUN 0's
path, the address it listens on, and either no authentication or CHAP's
user and secret (12 to 16 characters). The whole of `ctl.conf` can be
edited below it; saving writes it, root's alone as it may hold CHAP
secrets, and has ctld read it again. Under it, what `ctladm(8)` says of
the LUNs, the sessions and the ports.

`arcanactl iscsi conf FILE` and `arcanactl iscsi enable yes`.

## HAST

Highly Available Storage: `hastd(8)` replicates a provider (a disk, a
partition) to another host block by block; the primary's
`/dev/hast/NAME` is used as a disk, by UFS or ZFS, and CARP (Network)
or a script moves the primary role on failure. **Enable and start
hastd** turns it on.

`/etc/hast.conf` (`hast.conf(5)`), the same on both hosts, names each
resource and, for each host, its local provider and the other's
address. Each resource has **Create** (`hastctl create`: its metadata
written on the provider, which loses what it held, asked first) and
**Primary**, **Secondary** and **Init**, its role (`hastctl role`).
Under them, `hastctl status` and `hastctl list`.

`arcanactl hast conf FILE`, `hast create NAME`, `hast role primary NAME`.
