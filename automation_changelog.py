import sys
import os.path
import time
import getopt

deb_template = '''{0} ({1}+vmware.1-1) stable; urgency=optional

  * Upstream release: https://github.com/{2}/releases/tag/v{3}
  * VMware release: https://github.com/heptio/{4}/releases/tag/v{5}+vmware.1

 -- VMware Release Engineering <release-engineering@heptio.com>  {6}'''

rpm_template = '''* {0} VMware Release Engineering <release-engineering@heptio.com>  - {1}-1.vmware.1
- Upstream release: https://github.com/{2}/releases/tag/v{3}
- VMware release: https://github.com/heptio/{4}/releases/tag/v{5}+vmware.1'''

def get_path_and_url(repo):
    debpath = []
    rpmpath = ""
    upstream_url = ""
    if repo == "kubernetes":
        for i in ["kubeadm", "kubelet", "kubectl"]:
            debpath.append("kubernetes/debs/xenial/" + i + "/debian")
        rpmpath = "kubernetes/rpms/specs"
        upstream_url = "kubernetes/kubernetes"
    elif repo == "cni-plugins":
        debpath.append("cni-plugins/debs/xenial/kubernetes-cni/debian")
        rpmpath = "cni-plugins/rpms/specs"
        upstream_url = "containernetworking/plugins"
    elif repo == "cri-tools":
        debpath.append("cri-tools/debs/xenial/cri-tools/debian")
        rpmpath = "cri-tools/rpms/specs"
        upstream_url = "kubernetes-incubator/cri-tools"
    else:
        sys.stderr.write("Can't recognize repo!" + "\n")
        raise SystemExit(1)
    return debpath, rpmpath, upstream_url


def write_debs(path, major_minor, version, upstream_url, repo):
    for p in path:
        filename = p + "/changelog-" + major_minor
        s = p.split("/")
        debname = s[-2:-1][0]
        current_time = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime())
        args = [debname, version, upstream_url, version, repo, version, current_time]
        if not os.path.isfile(filename):
            with open(filename, "w") as f:
                f.write(deb_template.format(*args))
                f.close()
        else:
            with open(filename, 'r') as f:
                lines = f.readlines()
                f.close()
            with open(filename, 'w') as n:
                n.write(deb_template.format(*args))
                n.write("\n\n")
                n.writelines(lines)
                n.close()

def write_rpms(path, major_minor, version, upstream_url, repo):
    filename = path + "/changelog-" + major_minor
    current_time = time.strftime("%a %b %d %Y", time.localtime())
    args = [current_time, version, upstream_url, version, repo, version]
    if not os.path.isfile(filename):
        with open(filename, "w") as f:
            f.write(rpm_template.format(*args))
            f.close()
    else:
        with open(filename, 'r') as f:
            lines = f.readlines()
            f.close()
        with open(filename, 'w') as n:
            n.write(rpm_template.format(*args))
            n.write("\n\n")
            n.writelines(lines)
            n.close()


def parse_version(version):
    s = version.split(".")
    major_minor = ".".join(s[:2])
    return major_minor

def usage():
    print("Example: python3 automation_changelog.py -r kubernetes -v 1.15.0")

if __name__ == '__main__':
    try:
        options, args = getopt.getopt(sys.argv[1:], "hr:v:", ["help", "repo=", "version="])
    except getopt.GetoptError:
        print("Please check usage by -h or --help flag")
        usage()
        raise SystemExit(1)
    for name, value in options:
        if name in ("-h", "--help"):
            usage()
            raise SystemExit(1)
        if name in ("-r", "--repo"):
            repo = value
        if name in ("-v", "--version"):
            version = value
    try:
        major_minor = parse_version(version)
        debpath, rpmpath, upstream_url = get_path_and_url(repo)
        write_debs(debpath, major_minor, version, upstream_url, repo)
        write_rpms(rpmpath, major_minor, version, upstream_url, repo)
    except Exception as e:
        print(e)
        print("Usage: \n")
        usage()
