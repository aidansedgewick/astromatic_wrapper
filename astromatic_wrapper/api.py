# Copyright 2015 Fred Moolekamp
# BSD 3-clause license
"""
API for E. Bertin's Astromatic software suite
"""
import subprocess
import os
import logging
import warnings
import traceback

logger = logging.getLogger('astromatic.api')

codes = {
    #'Eye': 'eye', 
    #'MissFITS': 'missfits', 
    'PSFEx': 'psfex', 
    'SCAMP': 'scamp', 
    'SExtractor': 'sex', 
    #'SkyMaker': '', 
    #'STIFF': 'stiff',
    #'Stuff': '',
    'SWarp': 'swarp',
    #'WeightWatcher': 'ww'
}

def run_sex(pipeline, step_id, files, api_kwargs={}, frames=[]):
    """
    Run SExtractor with a specified set of parameters.
    
    Parameters
    ----------
    pipeline: `astromatic_wrapper.utils.pipeline.Pipeline`
        Pipeline containing parameters that may be necessary to set certain 
        AstrOmatic configuration parameters
    step_id: str
        Unique identifier for the current step in the pipeline
    files: dict
        Dict of filenames for fits files to use in sextractor. Possible keys are:
            * image: filename of the fits image (required)
            * dqmask: filename of a bad mixel mask for the given image (optional)
            * wtmap: filename of a weight map for the given image (optional)
    kwargs: dict
        Keyword arguements to pass to ``atrotoyz.Astromatic.run`` or
        ``astrotoyz.Astromatic.run_sex_frames``
    frames: list of integers (optional)
        Only run sextractor on a specific set of frames. The default value is an empty list,
        which runs SExtractor without specifying any frames
    
    Returns
    -------
    result: dict
        Result of the astromatic code execution. This will minimally contain a ``status``
        key, that indicates ``success`` or ``error``. Additional keys:
        - error_msg: str
            If there is an error and the user is storing the output or exporting XML metadata,
            ``error_msg`` will contain the error message generated by the code
        - output: str
            If ``store_output==True`` the output of the program execution is
            stored in the ``output`` value.
        - warnings: str
            If the WRITE_XML parameter is ``True`` then a table of warnings detected
            in the code is returned
    """
    if 'code' not in api_kwargs:
        api_kwargs['code'] = 'SExtractor'
    if 'cmd' not in api_kwargs and 'SExtractor' in pipeline.build_paths:
        api_kwargs['cmd'] = pipeline.build_paths['SExtractor']
    if 'temp_path' not in api_kwargs:
        api_kwargs['temp_path'] = pipeline.paths['temp']
    if 'config' not in api_kwargs:
        api_kwargs['config'] = {}
    if 'CATALOG_NAME' not in api_kwargs['config']:
        api_kwargs['config']['CATALOG_NAME'] = files['image'].replace('.fits', '.cat')
    if 'FLAG_IMAGE' not in api_kwargs['config'] and 'dqmask' in files:
        api_kwargs['config']['FLAG_IMAGE'] = files['dqmask']
    if 'WEIGHT_IMAGE' not in api_kwargs['config'] and 'wtmap' in files:
        api_kwargs['config']['WEIGHT_IMAGE'] = files['wtmap']
    if 'log' in pipeline.paths:
        if 'WRITE_XML' not in api_kwargs['config']:
            api_kwargs['config']['WRITE_XML'] = 'Y'
        if 'XML_NAME' not in api_kwargs['config']:
            api_kwargs['config']['XML_NAME'] = os.path.join(pipeline.paths['log'], 
                '{0}.sex.log.xml'.format(step_id))
    sex = Astromatic(**api_kwargs)
    if len(frames)==0:
        result = sex.run(files['image'])
    else:
        result = sex.run_frames(files['image'], 'SExtractor', frames, False)
    return result
    
def run_scamp(pipeline, step_id, catalogs, api_kwargs={}, save_catalog=None):
    """
    Run SCAMP with a specified set of parameters
    
    Parameters
    ----------
    pipeline: `astromatic_wrapper.utils.pipeline.Pipeline`
        Pipeline containing parameters that may be necessary to set certain 
        AstrOmatic configuration parameters
    step_id: str
        Unique identifier for the current step in the pipeline
    catalogs: list
        List of catalog names used to generate astrometric solution
    api_kwargs: dict
        Dictionary of keyword arguments used to run SCAMP
    save_catalog: str (optional)
        If ``save_catalog`` is specified, the reference catalog used to generate the
        solution will be save to the path ``save_catalog``.
    
    Returns
    -------
    result: dict
        Result of the astromatic code execution. This will minimally contain a ``status``
        key, that indicates ``success`` or ``error``. Additional keys:
        - error_msg: str
            If there is an error and the user is storing the output or exporting XML metadata,
            ``error_msg`` will contain the error message generated by the code
        - output: str
            If ``store_output==True`` the output of the program execution is
            stored in the ``output`` value.
        - warnings: str
            If the WRITE_XML parameter is ``True`` then a table of warnings detected
            in the code is returned
    """
    if 'code' not in api_kwargs:
        api_kwargs['code'] = 'SCAMP'
    if 'cmd' not in api_kwargs and 'SCAMP' in pipeline.build_paths:
        api_kwargs['cmd'] = pipeline.build_paths['SCAMP']
    if 'temp_path' not in api_kwargs:
        api_kwargs['temp_path'] = pipeline.paths['temp']
    if 'config' not in api_kwargs:
        api_kwargs['config'] = {}
    if save_catalog is not None:
        api_kwargs['config']['SAVE_REFCATALOG'] = 'Y'
        api_kwargs['config']['REFOUT_CATPATH'] = save_catalog
    if 'log' in pipeline.paths:
        if 'WRITE_XML' not in api_kwargs['config']:
            api_kwargs['config']['WRITE_XML'] = 'Y'
        if 'XML_NAME' not in api_kwargs['config']:
            api_kwargs['config']['XML_NAME'] = os.path.join(pipeline.paths['log'], 
                '{0}.scamp.log.xml'.format(step_id))
    scamp = Astromatic(**api_kwargs)
    result = scamp.run(catalogs)
    return result
    
def run_swarp(pipeline, step_id, filenames, api_kwargs, frames=[]):
    """
    Run SWARP with a specified set of parameters
    
    Parameters
    ----------
    pipeline: `astromatic_wrapper.utils.pipeline.Pipeline`
        Pipeline containing parameters that may be necessary to set certain 
        AstrOmatic configuration parameters
    step_id: str
        Unique identifier for the current step in the pipeline
    filenames: list
        List of filenames that are stacked together
    api_kwargs: dict
        Keyword arguments used to run SWARP
    frames: list (optional)
        Subset of frames to stack. Default value is an empty list, which runs SWarp on
        without specifying any frames
    
    Returns
    -------
    result: dict
        Result of the astromatic code execution. This will minimally contain a ``status``
        key, that indicates ``success`` or ``error``. Additional keys:
        - error_msg: str
            If there is an error and the user is storing the output or exporting XML metadata,
            ``error_msg`` will contain the error message generated by the code
        - output: str
            If ``store_output==True`` the output of the program execution is
            stored in the ``output`` value.
        - warnings: str
            If the WRITE_XML parameter is ``True`` then a table of warnings detected
            in the code is returned
    """
    if 'code' not in api_kwargs:
        api_kwargs['code'] = 'SWarp'
    if 'cmd' not in api_kwargs and 'SWARP' in pipeline.build_paths:
        api_kwargs['cmd'] = pipeline.build_paths['SWARP']
    if 'temp_path' not in api_kwargs:
        api_kwargs['temp_path'] = pipeline.paths['temp']
    if 'config' not in api_kwargs:
        api_kwargs['config'] = {}
    if 'RESAMPLE_DIR' not in api_kwargs['config']:
        api_kwargs['config']['RESAMPLE_DIR'] = api_kwargs['temp_path']
    #if 'IMAGEOUT_NAME' not in api_kwargs['config']:
    #    raise PipelineError('Must include a name for the new stacked image')
    if 'log' in pipeline.paths:
        if 'WRITE_XML' not in api_kwargs['config']:
            api_kwargs['config']['WRITE_XML'] = 'Y'
        if 'XML_NAME' not in api_kwargs['config']:
            api_kwargs['config']['XML_NAME'] = os.path.join(pipeline.paths['log'], 
                '{0}.swarp.log.xml'.format(step_id))
    swarp = Astromatic(**api_kwargs)
    if len(frames)==0:
        result = swarp.run(filenames)
    else:
        result = swarp.run_frames(filenames, 'SWarp', frames, False)
    return result
    
def run_psfex(pipeline, step_id, catalogs, api_kwargs={}):
    """
    Run PSFEx with a specified set of parameters.
    
    Parameters
    ----------
    pipeline: `astromatic_wrapper.utils.pipeline.Pipeline`
        Pipeline containing parameters that may be necessary to set certain 
        AstrOmatic configuration parameters
    step_id: str
        Unique identifier for the current step in the pipeline
    catalogs: str or list
        catalog filename (or list of catalog filenames) to use
    api_kwargs: dict
        Keyword arguements to pass to PSFEx
    
    Returns
    -------
    result: dict
        Result of the astromatic code execution. This will minimally contain a ``status``
        key, that indicates ``success`` or ``error``. Additional keys:
        - error_msg: str
            If there is an error and the user is storing the output or exporting XML metadata,
            ``error_msg`` will contain the error message generated by the code
        - output: str
            If ``store_output==True`` the output of the program execution is
            stored in the ``output`` value.
        - warnings: str
            If the WRITE_XML parameter is ``True`` then a table of warnings detected
            in the code is returned
    """
    if 'code' not in api_kwargs:
        api_kwargs['code'] = 'PSFEx'
    if 'cmd' not in api_kwargs and 'PSFEx' in pipeline.build_paths:
        api_kwargs['cmd'] = pipeline.build_paths['PSFEx']
    if 'temp_path' not in api_kwargs:
        api_kwargs['temp_path'] = pipeline.paths['temp']
    if 'config' not in api_kwargs:
        api_kwargs['config'] = {}
    if 'PSF_DIR' not in api_kwargs['config']:
        api_kwargs['config']['PSF_DIR'] = pipeline.paths['temp']
    if 'log' in pipeline.paths:
        if 'WRITE_XML' not in api_kwargs['config']:
            api_kwargs['config']['WRITE_XML'] = 'Y'
        if 'XML_NAME' not in api_kwargs['config']:
            api_kwargs['config']['XML_NAME'] = os.path.join(pipeline.paths['log'], 
                '{0}.psfex.log.xml'.format(step_id))
    psfex = Astromatic(**api_kwargs)
    result = psfex.run(catalogs)
    return result

class AstromaticError(Exception):
    def __init__(self,msg):
        self.msg=msg
        self.traceback=traceback.format_exc()
    def __str__(self):
        return self.traceback+'\n'+self.msg+'\n'

class Astromatic:
    """
    Class to hold config options for an Astrometric code. 
    """
    def __init__(self, code, temp_path=None, config={}, config_file=None, store_output=False, 
            **kwargs):
        """
        Initialize a particular astromatic code with a given set of configurations.
        
        Parameters
        ----------
        code: str
            Name of the code to use
        temp_path: str
            Path to store temporary files generated by the astromatic code (such as 
            resamp files in SWarp)
        config: dict (optional)
            Dictionary of configuration options to pass in the command line.
        config_file: str (optional)
            Name of the configuration file to use. If none is specified, the default
            config file for the given code is used
        store_output: boolean (optional)
            If ``store_output`` is ``False``, the output of the code is printed to 
            sys.stdout. If ``store_output`` is ``True`` the output is saved in a variable
            that is returned when the function is run.
        """
        self.code = code
        if code not in codes:
            warnings.warn("'{0} not in Astromatic codes, you will need to specify " +
                "a 'cmd' to run".format(code))
        self.temp_path = temp_path
        self.config = config
        self.config_file = config_file
        self.store_output = store_output
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def build_cmd(self, filenames, **kwargs):
        """
        Build a command to run an astromatic code.
        
        Parameters
        ----------
        filenames: str or list
            Name of a file or list of filenames to run in the command line statement
        **kwargs: keyword arguments
            The following are optional keyword arguments that may be used:
                - code: str
                    Name of the astromatic code to use. This should be contained in 
                    ``astrotoyz.astromatic.api.codes``
                - config: dict (optional)
                    Dictionary of configuration options to pass in the command line.
                - config_file: str (optional)
                    Name of the configuration file to use. If none is specified, the default
                    config file for the given code is used
        
        Returns
        -------
        cmd: str
            Commandline statement to run the given code
        kwargs: dict
            Dictionary of keyword arguments used in the build
        """
        # If a single catalog is passed, convert to an array
        if not isinstance(filenames, list):
            filenames = [filenames]
        # Update kwargs with any missing variables
        for attr, attr_val in vars(self).items():
            if attr not in kwargs:
                kwargs[attr] = attr_val
        logger.debug("kwargs used to build command:\n{0}".format(kwargs))
        # If the user did not specify a params file, create one in the temp directory and 
        # update the config parameters
        if kwargs['code']=='SExtractor':
            if 'params' in kwargs:
                if 'PARAMETERS_NAME' in kwargs['config']:
                    warnings.warn("Multiple parameter files specified, using 'params'")
                if 'temp_path' not in kwargs:
                    raise AstromaticError(
                        "You must either supply a 'PARAMETERS_NAME' in 'config' or "+
                        "a 'temp_path' to store the temporary parameters file")
                param_name = os.path.join(kwargs['temp_path'], 'sex.param')
                f = open(param_name, 'w')
                for p in kwargs['params']:
                    f.write(p+'\n')
                f.close()
                kwargs['config']['PARAMETERS_NAME'] = param_name
            elif 'PARAMETERS_NAME' not in kwargs['config']:
                raise AstromaticError(
                    "To run SExtractor yo must either supply a 'params' list of parameters "+
                    "or a config keyword 'PARAMETERS_NAME' that points to a parameters file")
        # Get the correct command for the given code (if one is not specified)
        if 'cmd' not in kwargs:
            if kwargs['code'] not in codes:
                raise AstromaticError(
                    "You must either supply a valid astromatic 'code' name or "+
                    "a 'cmd' to run")
            cmd = codes[kwargs['code']]
        else:
            cmd = kwargs['cmd']
        if cmd[-1]!=' ':
            cmd += ' '
        # Append the filename(s) that are run by the code
        cmd += ' '.join(filenames)
        # If the user specified a config file, use it
        if kwargs['config_file'] is not None:
            cmd += ' -c '+kwargs['config_file']
        # Add on any user specified parameters
        for param in kwargs['config']:
            if isinstance(kwargs['config'][param], bool):
                if kwargs['config'][param]:
                    val='Y'
                else:
                    val='N'
            else:
                val = kwargs['config'][param]
            cmd += ' -'+param+' '+val
        return (cmd, kwargs)
    
    def _run_cmd(self, this_cmd, store_output=False, xml_name=None, raise_error=True, frame=None):
        """
        Execute a command to run an astromatic code. Since this allows a user to
        run any command on the host, it is recommended that no public
        interface gives a user access to this method.
        
        Parameters
        ----------
        this_cmd: str
            The command to run from a subprocess. 
        store_output: bool (optional)
            Whether to store the output and return it to the user or print the output
            to the screen.
        xml_name: str (optional)
            If the config file instructs the code to save an xml file (recommended)
            this is the name of the xml file (used to detect error messages and warnings)
        raise_error: bool
            If ``raise_error==True``, python will raise an error if the 
            astromatic code fails due to an error
        
        Returns
        -------
        result: dict
            Result of the astromatic code execution. This will minimally contain a ``status``
            key, that indicates ``success`` or ``error``. Additional keys:
            - error_msg: str
                If there is an error and the user is storing the output or exporting XML metadata,
                ``error_msg`` will contain the error message generated by the code
            - output: str
                If ``store_output==True`` the output of the program execution is
                stored in the ``output`` value.
            - warnings: str
                If the WRITE_XML parameter is ``True`` then a table of warnings detected
                in the code is returned
        """
        result = {'status':'success'}
        # Run code
        logger.info('cmd:\n{0}\n'.format(this_cmd))
        if store_output:
            p = subprocess.Popen(this_cmd, shell=True, stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT)
            output = p.stdout.readlines()
            result['output'] = output
            for line in output:
                if 'error' in line.lower():
                    result['status'] = 'error'
                    result['error_msg'] = line
                    break
        else:
            status = subprocess.call(this_cmd, shell=True)
            if status>0:
                result['status'] = 'error'
                if xml_name is not None:
                    from astropy.io.votable import parse
                    votable = parse(xml_name)
                    for param in votable.resources[0].resources[0].params:
                        if param.name=='Error_Msg':
                            result['error_msg'] = param.value
        # Log any warnings generated by the astromatic code
        if xml_name is not None:
            # SExtractor logs have a '-1' added to the filename and also
            # stream the output catalog to the votable. Since the output may
            # be a FITS_LDAC file, astropy does not rad this properly and it
            # causes the read to crash. This code removes the link to the FITS_LDAC file
            if frame is not None:
                xml_name = xml_name.replace('.xml','-{0}.xml'.format(frame))
            if self.code == 'SExtractor':
                f = open(xml_name, 'r')
                all_lines = f.readlines()
                f.close()
                f = open(xml_name, 'w')
                for line in all_lines:
                    if '<fits' not in line.lower():
                        f.write(line)
                    elif '</DATA>' in line.upper():
                        f.write('</DATA>\n')
                f.close()
            
            from astropy.table import Table
            from astropy.io.votable import parse
            # Sometimes the xml file does not fit the VOTABLE standard,
            # so we mask the invalid parameters
            votable = parse(xml_name, invalid='mask', pedantic=False)
            result['warnings'] = Table.read(votable, table_id='Warnings', format='votable')
            # Fill in the masked values (otherwise there are problems with 
            # pipeline pickling)
            result['warnings'] = result['warnings'].filled(0)
            result['warnings'].meta['filename'] = xml_name
        # Raise an Exception if appropriate
        if result['status'] == 'error' and raise_error:
            error_msg = "Error in '{0}' execution".format(self.code)
            if 'error_msg' in result:
                error_msg += ': {0}'.format(result['error_msg'])
            raise AstromaticError(error_msg)
        return result
    
    def run(self, filenames, store_output=False, raise_error=True, **kwargs):
        """
        Build the command and run the code with a given set of options. If one of the
        keyword arguments is ``store_output=True`` the output of the code is returned,
        otherwise the status of the codes execution is returned.
        
        Parameters
        ----------
        filenames: str or list
            Name of a file or list of filenames to run in the command line statement
        store_output: bool (optional)
            Whether to store the output and return it to the user or print the output
            to the screen.
        raise_error: bool (optional)
            If ``raise_error==True``, python will raise an error if the 
            astromatic code fails due to an error
        **kwargs: keyword arguments
            The following are optional keyword arguments that may be used:
                - code: str
                    Name of the astromatic code to use. This should be contained in 
                    ``astrotoyz.astromatic.api.codes``
                - config: dict (optional)
                    Dictionary of configuration options to pass in the command line.
                - config_file: str (optional)
                    Name of the configuration file to use. If none is specified, the default
                    config file for the given code is used
        
        Returns
        -------
        result: dict
            Result of the astromatic code execution. This will minimally contain a ``status``
            key, that indicates ``success`` or ``error``. Additional keys:
            - error_msg: str
                If there is an error and the user is storing the output or exporting XML metadata,
                ``error_msg`` will contain the error message generated by the code
            - output: str
                If ``store_output==True`` the output of the program execution is
                stored in the ``output`` value.
            - warnings: str
                If the WRITE_XML parameter is ``True`` then a table of warnings detected
                in the code is returned
        """
        this_cmd, kwargs = self.build_cmd(filenames, **kwargs)
        if ('WRITE_XML' in kwargs['config'] and 'XML_NAME' in kwargs['config']
                        and kwargs['config']['WRITE_XML'] == 'Y'):
            xml_name = kwargs['config']['XML_NAME']
        else:
            xml_name = None
        
        return self._run_cmd(this_cmd, store_output, xml_name, raise_error)
    
    def run_frames(self, filenames, code=None, frames=[1], raise_error=True,
            **kwargs):
        """
        If the user is running sextractor on an individual frame, this command will
        correctly add the frame to the image filename, flag filename, and weightmap filename
        (if they are specified).
        
        Parameters
        ----------
        filenames: str or list
            Name of a file or list of filenames to run in the command line statement
        code: str (optional)
            Name of the astromatic code to use. This should be contained in 
            ``astrotoyz.astromatic.api.codes`` and defaults to ``Astromatic.code``.
        frames: list (optional)
            Subset of AstrOmatic code to use. Defaults to ``[1]``.
        raise_error: bool (optional)
            If ``raise_error==True``, python will raise an error if the 
            astromatic code fails due to an error
        **kwargs: keyword arguments
            The following are optional keyword arguments that may be used:
                - config: dict (optional)
                    Dictionary of configuration options to pass in the command line.
                - config_file: str (optional)
                    Name of the configuration file to use. If none is specified, the default
                    config file for the given code is used
        
        Returns
        -------
        result: dict
            Result of the astromatic code execution. This will minimally contain a ``status``
            key, that indicates ``success`` or ``error``. Additional keys:
            - error_msg: str
                If there is an error and the user is storing the output or exporting XML metadata,
                ``error_msg`` will contain the error message generated by the code
            - output: str
                If ``store_output==True`` the output of the program execution is
                stored in the ``output`` value.
            - warnings: str
                If the WRITE_XML parameter is ``True`` then a table of warnings detected
                in the code is returned
        """
        # Set the code to run
        if code is None:
            code = self.code
        # Format any filenames that may need a frame specified
        if 'config' not in kwargs:
            kwargs['config'] = self.config
        flag_img = None
        weight_img = None
        if code == 'SExtractor':
            if 'FLAG_IMAGE' in kwargs['config']:
                flag_img = kwargs['config']['FLAG_IMAGE']
            if 'WEIGHT_IMAGE' in kwargs['config']:
                weight_img = kwargs['config']['WEIGHT_IMAGE']
        elif code !='SWarp':
            raise AstromaticError("The code you have specified is not currently supported "
                "using individual frames")
        if('WRITE_XML' in kwargs['config'] and kwargs['config']['WRITE_XML'] and
                'XML_NAME' in kwargs['config']):
            xml_name = kwargs['config']['XML_NAME']
        else:
            xml_name = None
        # Build the command
        this_cmd, kwargs = self.build_cmd(filenames, code=code, **kwargs)
        
        # For each frame, modify the command to include the frames and run the code
        all_warnings = None
        for frame in frames:
            new_cmd = this_cmd
            frame_str = '['+str(frame)+']'
            
            # Convert all multi-extension files to filenames with the same frame specified
            if not isinstance(filenames, list):
                filenames = [filenames]
            for filename in filenames:
                new_cmd = new_cmd.replace(filename, filename+frame_str)
            if flag_img is not None:
                new_cmd = new_cmd.replace(flag_img, flag_img+frame_str)
            if weight_img is not None:
                new_cmd = new_cmd.replace(weight_img, weight_img+frame_str)
            if xml_name is not None:
                new_cmd = new_cmd.replace(xml_name, xml_name.replace(
                    '.xml', '-'+str(frame)+'.xml'))
            # Run the code
            result = self._run_cmd(new_cmd, False, xml_name, raise_error, frame=str(frame))
            
            # Combine all warnings into a single table
            if 'warnings' in result and len(result['warnings'])>0:
                from astropy.table import vstack
                warnings = result['warnings']
                warnings['frame'] = frame
                if all_warnings is None:
                    all_warnings = warnings
                else:
                    all_warnings = vstack([all_warnings, warnings])
        
        result = {
            'status': 'success',
            'warnings': all_warnings
        }
        return result
    
    def get_version(self, cmd=None):
        """
        Get the version of the currently loaded astromatic code
        
        Parameters
        ----------
        cmd: str (optional)
            Name of the command to run. If this isn't specified it will use the cmd
            specified when the ``Astromatic`` class was initialized. This is usually
            just the code to run (for example 'sex', 'scamp', 'swarp', 'psfex', ...)
            but occationally if the user doesn't have root privilages this may be
            another location (for example ``~/astromatic/bin/sex``).
        Retruns
        -------
        version: str
            Version of the specified astromatic code
        date: str
            Date associated with the specified astromatic code
        """
        # Get the correct command for the given code (if one is not specified)
        if cmd is None:
            if self.code not in codes:
                raise AstromaticError(
                    "You must either supply a valid astromatic 'code' name or a 'cmd'")
            cmd = codes[self.code]
        if cmd[-1]!=' ':
            cmd += ' '
        cmd += '-v'
        try:
            p = subprocess.Popen('sex', shell=True, stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT)
        except:
            raise AstromaticError("Unable to run '{0}'. "
                "Please check that it is installed correctly".format(cmd))
        for line in p.stdout.readlines():
            line_split = line.split()
            line_split = map(lambda x: x.lower(), line_split)
            if 'version' in line_split:
                version_idx = line_split.index('version')
                version = line_split[version_idx+1]
                date = line_split[version_idx+2]
                date = date.lstrip('(').rstrip(')')
                break
        return version, date