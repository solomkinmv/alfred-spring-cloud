import plistlib
import sys

plist_location = u'../info.plist'
version_location = u'../version'


def update_plist(version):
    info = plistlib.readPlist(plist_location)
    previous_version = info['version']
    print("Previous version is: " + previous_version)

    if previous_version == version:
        print('Version is the same. Please update "version" file with the new version.')
        raise ValueError

    info['version'] = version
    plistlib.writePlist(info, plist_location)


def main():
    try:
        with open(version_location) as f:
            version = f.read()
            print("Current version is: " + version)

        update_plist(version)
    except Exception as e:
        print("Failed to update version: " + str(e))
        return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())
