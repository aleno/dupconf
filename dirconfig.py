import os

class DirConfiguration:

    def __init__ (self, path, recursive=True, debug=False):
        if not os.path.exists(path):
            raise ValueError ('Path does not exist')
        elif not os.path.isdir(path):
            raise ValueError ('Path is not a directory')

        self.path = path
        self.recursive = recursive
        self.debug = debug
        self.config = self.__read_path(path, recursive=recursive)

    def __read_path (self, rootPath, config={}, recursive=True):
        paths = os.listdir(rootPath)
        for currPath in paths:
            currPath = rootPath + "/" + currPath
            key = os.path.basename(currPath)
            if self.debug: print 'this is for path', currPath

            if os.path.isdir(currPath) and recursive:
                value = self.__read_path(currPath, {}, recursive)
                if self.debug: print 'for key ' + key + ' storing child value:', value
                config[key] = value

            elif os.path.isfile(currPath):
                currFile = open(currPath, 'r')
                key = os.path.basename(currPath)

                if key == 'children':
                    if self.debug: print 'Warning: illegal file name in "'+currPath+'":', key
                else:
                    for currLine in currFile:
                        if key not in config:
                            config[key] = []

                        if self.debug: print 'for key ' + key + ' storing:', currLine.strip()
                        config[key].append(currLine.strip())

            else:
                if self.debug: print 'Notice: odd path exists in configuration directory:', currPath

        if self.debug: print 'returning this for path "' + rootPath + '":', config
        return config
