import sys
import os.path
import time
import getopt

deb_template = '''{0} ({1}+vmware.{8}-1) stable; urgency=optional

  * Upstream release: https://github.com/{2}/releases/tag/v{3}
  * VMware release: https://github.com/heptio/{4}/releases/tag/v{5}+vmware.{9}

 -- VMware Release Engineering <{6}>  {7}'''

rpm_template = '''* {0} VMware Release Engineering <{1}>  - {2}-1.vmware.{7}
- Upstream release: https://github.com/{3}/releases/tag/v{4}
- VMware release: https://github.com/heptio/{5}/releases/tag/v{6}+vmware.{8}'''

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


def write_debs(path, major_minor, version, vversion, upstream_url, repo, email):
    for p in path:
        filename = p + "/changelog-" + major_minor
        s = p.split("/")
        debname = s[-2:-1][0]
        current_time = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime())
        args = [debname, version, upstream_url, version, repo, version, email, current_time, vversion, vversion]
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

def write_rpms(path, major_minor, version, vversion, upstream_url, repo, email):
    filename = path + "/changelog-" + major_minor
    current_time = time.strftime("%a %b %d %Y", time.localtime())
    args = [current_time, email, version, upstream_url, version, repo, version, vversion, vversion]
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

def write_version_control_file(isgobuild, major_minor, version, vversion):
    fit_version_control_file = ""
    if isgobuild:
        path = "essentialpks_release/"
    else:
        path = "publish-release/"
    for file in os.listdir(path):
        if major_minor in file:
            fit_version_control_file = os.path.join(path, file)
            break
    if not fit_version_control_file:
        print("We don't support generating minor release!")
        sys.exit(1)
    new_version_control_file = path + "essentialpks-v" + version + "+vmware." + vversion
    with open(fit_version_control_file, 'r') as f:
        lines = f.readlines()
        f.close()
    with open(new_version_control_file, 'w') as n:
        for line in lines:
            if "kubernetes" in line:
                n.writelines("kubernetes=v" + version + "+vmware." + vversion + "\n")
            else:
                n.writelines(line)
        n.close()
    

def parse_version(version):
    s = version.split(".")
    major_minor = ".".join(s[:2])
    return major_minor

def usage():
    print('''usage: python3 automation_changelog.py [option] ... [-r | -v | --file ] [arg]
Options and arguments :
-v, --version : version; e.g. 1.14.2
--vversion : vmware version; e.g. 1
-r, --repo    : kubernetes, etcd, cni-plugins, cri-tools or coredns
-h, --help    : print help message and exit (also --help)
-e, --email   : email for changelog
-g      : is gobuild environment
--file  : create new version control file
''')

if __name__ == '__main__':
    isgobuild = False
    generate_version_file = False
    try:
        options, args = getopt.getopt(sys.argv[1:], "hr:v:ge:", ["help", "repo=", "version=", "vversion=", "file", "email="])
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
            continue
        if name in ("-v", "--version"):
            version = value
            continue
        if name in ("--vversion"):
            vversion = value
            continue
        if name in ("-g",):
            isgobuild = True
            continue
        if name in ("--file,"):
            generate_version_file = True
            continue
        if name in ("-e", "--email,"):
            email = value
            continue

    try:
        major_minor = parse_version(version)
        debpath, rpmpath, upstream_url = get_path_and_url(repo)
        write_debs(debpath, major_minor, version, vversion, upstream_url, repo, email)
        write_rpms(rpmpath, major_minor, version, vversion, upstream_url, repo, email)
        if generate_version_file:
            write_version_control_file(isgobuild, major_minor, version, vversion)
    except Exception as e:
        print(e)
        print("Usage: \n")
        usage()
