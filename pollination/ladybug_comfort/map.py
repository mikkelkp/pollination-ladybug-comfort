"""Produce spatial maps of thermal conditions and comfort."""
from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class PmvMap(Function):
    """Get CSV files with maps of PMV comfort from EnergyPlus and Radiance results."""

    result_sql = Inputs.file(
        description='A SQLite file that was generated by EnergyPlus and contains '
        'hourly or sub-hourly thermal comfort results.',
        path='result.sql', extensions=['sql', 'db', 'sqlite']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    epw = Inputs.file(
        description='Weather file used to estimate conditions for any outdoor '
        'sensors and to compute sun positions.', path='weather.epw', extensions=['epw']
    )

    total_irradiance = Inputs.file(
        description='A Radiance .ill containing total irradiance for each sensor in '
        'the enclosure-info.', path='total.ill', extensions=['ill', 'irr']
    )

    direct_irradiance = Inputs.file(
        description='A Radiance .ill containing direct irradiance for each sensor in '
        'the enclosure-info.', path='direct.ill', extensions=['ill', 'irr']
    )

    ref_irradiance = Inputs.file(
        description='A Radiance .ill containing ground-reflected irradiance for each '
        'sensor in the enclosure-info.', path='ref.ill', extensions=['ill', 'irr']
    )

    sun_up_hours = Inputs.file(
        description='A sun-up-hours.txt file output by Radiance and aligns with the '
        'input irradiance files.', path='sun-up-hours.txt'
    )

    air_speed = Inputs.str(
        description='A single number for air speed in m/s or a string of a JSON array '
        'with numbers that align with the result-sql reporting period. This '
        'will be used for all indoor comfort evaluation.', default='0.1'
    )

    met_rate = Inputs.str(
        description='A single number for metabolic rate in met or a string of a '
        'JSON array with numbers that align with the result-sql reporting period.',
        default='1.1'
    )

    clo_value = Inputs.str(
        description='A single number for clothing level in clo or a string of a JSON '
        'array with numbers that align with the result-sql reporting period.',
        default='0.7'
    )

    solarcal_par = Inputs.str(
        description='A SolarCalParameter string to customize the assumptions of '
        'the SolarCal model.', default='--posture seated --sharp 135 '
        '--absorptivity 0.7 --emissivity 0.95'
    )

    comfort_par = Inputs.str(
        description='A PMVParameter string to customize the assumptions of '
        'the PMV comfort model.', default='--ppd-threshold 10'
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If None, the analysis '
        'will be for the entire result_sql run period.', default=''
    )

    write_set_map = Inputs.str(
        description='A switch to note whether the output temperature CSV should '
        'record Operative Temperature or Standard Effective Temperature (SET). '
        'SET is relatively intense to compute and so only recording Operative '
        'Temperature can greatly reduce run time, particularly when air speeds '
        'are low. However, SET accounts for all 6 PMV model inputs and so is a '
        'more representative "feels-like" temperature for the PMV model.',
        default='write-op-map',
        spec={'type': 'string', 'enum': ['write-op-map', 'write-set-map']}
    )

    @command
    def run_pmv_map(self):
        return 'ladybug-comfort map pmv result.sql enclosure_info.json ' \
            'weather.epw --total-irradiance total.ill --direct-irradiance direct.ill ' \
            '--ref-irradiance ref.ill --sun-up-hours sun-up-hours.txt ' \
            '--air-speed "{{self.air_speed}}" --met-rate "{{self.met_rate}}" ' \
            '--clo-value "{{self.clo_value}}" --solarcal-par "{{self.solarcal_par}}" ' \
            '--comfort-par "{{self.comfort_par}}" --run-period "{{self.run_period}}" ' \
            '--{{self.write_set_map}}  --folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output CSV files.', path='output'
    )

    temperature_map = Outputs.file(
        description='CSV file containing a map of Operative Temperature (To) or '
        'Standard Effective Temperature (SET) for each sensor and step of the analysis.'
        'The write-set-map input determines which of the two metrics this file '
        'contains.', path='output/temperature.csv'
    )

    condition_map = Outputs.file(
        description='CSV file containing a map of comfort conditions for each '
        'sensor and step of the analysis. -1 indicates unacceptably cold conditions. '
        '+1 indicates unacceptably hot conditions. 0 indicates neutral (comfortable) '
        'conditions.', path='output/condition.csv'
    )

    pmv_map = Outputs.file(
        description='CSV file containing the Predicted Mean Vote (PMV) for each '
        'sensor and step of the analysis. This can be used to understand not just '
        'whether conditions are acceptable but how uncomfortably hot or cold they are.',
        path='output/condition_intensity.csv'
    )


@dataclass
class AdaptiveMap(Function):
    """Get CSV files with maps of Adaptive comfort from EnergyPlus and Radiance results.
    """

    result_sql = Inputs.file(
        description='A SQLite file that was generated by EnergyPlus and contains '
        'hourly or sub-hourly thermal comfort results.',
        path='result.sql', extensions=['sql', 'db', 'sqlite']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    epw = Inputs.file(
        description='Weather file used to estimate conditions for any outdoor '
        'sensors and to provide prevailing outdoor temperature for the adaptive '
        'comfort model.', path='weather.epw', extensions=['epw']
    )

    total_irradiance = Inputs.file(
        description='A Radiance .ill containing total irradiance for each sensor in '
        'the enclosure-info.', path='total.ill', extensions=['ill', 'irr']
    )

    direct_irradiance = Inputs.file(
        description='A Radiance .ill containing direct irradiance for each sensor in '
        'the enclosure-info.', path='direct.ill', extensions=['ill', 'irr']
    )

    ref_irradiance = Inputs.file(
        description='A Radiance .ill containing ground-reflected irradiance for each '
        'sensor in the enclosure-info.', path='ref.ill', extensions=['ill', 'irr']
    )

    sun_up_hours = Inputs.file(
        description='A sun-up-hours.txt file output by Radiance and aligns with the '
        'input irradiance files.', path='sun-up-hours.txt'
    )

    air_speed = Inputs.str(
        description='A single number for air speed in m/s or a string of a JSON array '
        'with numbers that align with the result-sql reporting period. This '
        'will be used for all indoor comfort evaluation.', default='0.1'
    )

    solarcal_par = Inputs.str(
        description='A SolarCalParameter string to customize the assumptions of '
        'the SolarCal model.', default='--posture seated --sharp 135 '
        '--absorptivity 0.7 --emissivity 0.95'
    )

    comfort_par = Inputs.str(
        description='An AdaptiveParameter string to customize the assumptions of '
        'the Adaptive comfort model.', default='--standard ASHRAE-55'
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If None, the analysis '
        'will be for the entire result_sql run period.', default=''
    )

    @command
    def run_adaptive_map(self):
        return 'ladybug-comfort map adaptive result.sql enclosure_info.json ' \
            'weather.epw --total-irradiance total.ill --direct-irradiance direct.ill ' \
            '--ref-irradiance ref.ill --sun-up-hours sun-up-hours.txt ' \
            '--air-speed "{{self.air_speed}}" --solarcal-par "{{self.solarcal_par}}" ' \
            '--comfort-par "{{self.comfort_par}}" --run-period "{{self.run_period}}" ' \
            '--folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output CSV files.', path='output'
    )

    temperature_map = Outputs.file(
        description='CSV file containing a map of Operative Temperature for each '
        'sensor and step of the analysis.', path='output/temperature.csv'
    )

    condition_map = Outputs.file(
        description='CSV file containing a map of comfort conditions for each '
        'sensor and step of the analysis. -1 indicates unacceptably cold conditions. '
        '+1 indicates unacceptably hot conditions. 0 indicates neutral (comfortable) '
        'conditions.', path='output/condition.csv'
    )

    deg_from_neutral_map = Outputs.file(
        description='CSV file containing a map of the degrees Celsius from the '
        'adaptive comfort neutral temperature for each sensor and step of the '
        'analysis. This can be used to understand not just whether conditions are '
        'acceptable but how uncomfortably hot or cold they are.',
        path='output/condition_intensity.csv'
    )


@dataclass
class UtciMap(Function):
    """Get CSV files with maps of UTCI comfort from EnergyPlus and Radiance results."""

    result_sql = Inputs.file(
        description='A SQLite file that was generated by EnergyPlus and contains '
        'hourly or sub-hourly thermal comfort results.',
        path='result.sql', extensions=['sql', 'db', 'sqlite']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    epw = Inputs.file(
        description='Weather file used to estimate conditions for any outdoor '
        'sensors and to compute sun positions.', path='weather.epw', extensions=['epw']
    )

    total_irradiance = Inputs.file(
        description='A Radiance .ill containing total irradiance for each sensor in '
        'the enclosure-info.', path='total.ill', extensions=['ill', 'irr']
    )

    direct_irradiance = Inputs.file(
        description='A Radiance .ill containing direct irradiance for each sensor in '
        'the enclosure-info.', path='direct.ill', extensions=['ill', 'irr']
    )

    ref_irradiance = Inputs.file(
        description='A Radiance .ill containing ground-reflected irradiance for each '
        'sensor in the enclosure-info.', path='ref.ill', extensions=['ill', 'irr']
    )

    sun_up_hours = Inputs.file(
        description='A sun-up-hours.txt file output by Radiance and aligns with the '
        'input irradiance files.', path='sun-up-hours.txt'
    )

    wind_speed = Inputs.str(
        description='A single number for meteorological wind speed in m/s or a string '
        'of a JSON array with numbers that align with the result-sql reporting period. '
        'This will be used for all indoor comfort evaluation while the EPW wind speed '
        'will be used for the outdoors.', default='0.5'
    )

    solarcal_par = Inputs.str(
        description='A SolarCalParameter string to customize the assumptions of '
        'the SolarCal model.', default='--posture seated --sharp 135 '
        '--absorptivity 0.7 --emissivity 0.95'
    )

    comfort_par = Inputs.str(
        description='A UTCIParameter string to customize the assumptions of '
        'the UTCI comfort model.', default='--cold 9 --heat 26'
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If None, the analysis '
        'will be for the entire result_sql run period.', default=''
    )

    @command
    def run_utci_map(self):
        return 'ladybug-comfort map utci result.sql enclosure_info.json ' \
            'weather.epw --total-irradiance total.ill --direct-irradiance direct.ill ' \
            '--ref-irradiance ref.ill --sun-up-hours sun-up-hours.txt ' \
            '--wind-speed "{{self.wind_speed}}" --solarcal-par ' \
            '"{{self.solarcal_par}}" --comfort-par "{{self.comfort_par}}" ' \
            '--run-period "{{self.run_period}}" --folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output CSV files.', path='output'
    )

    temperature_map = Outputs.file(
        description='CSV file containing a map of Universal Thermal Climate Index '
        '(UTCI) temperatures for each sensor and step of the analysis.',
        path='output/temperature.csv'
    )

    condition_map = Outputs.file(
        description='CSV file containing a map of comfort conditions for each '
        'sensor and step of the analysis. -1 indicates unacceptably cold conditions. '
        '+1 indicates unacceptably hot conditions. 0 indicates neutral (comfortable) '
        'conditions.', path='output/condition.csv'
    )

    category_map = Outputs.file(
        description='CSV file containing a map of the heat/cold stress categories '
        'for each sensor and step of the analysis. -5 indicates extreme cold stress. '
        '+5 indicates extreme heat stress. 0 indicates no thermal stress. '
        'This can be used to understand not just whether conditions are '
        'acceptable but how uncomfortably hot or cold they are.',
        path='output/condition_intensity.csv'
    )


@dataclass
class IrradianceContribMap(Function):
    """Get .ill files with maps of irradiance contributions from dynamic windows."""

    result_sql = Inputs.file(
        description='A SQLite file that was generated by EnergyPlus and contains '
        'hourly or sub-hourly thermal comfort results.',
        path='result.sql', extensions=['sql', 'db', 'sqlite']
    )

    direct_specular = Inputs.file(
        description='A Radiance .ill file containing direct irradiance for the '
        'specular version of the aperture group.',
        path='direct_spec.ill', extensions=['ill', 'irr']
    )

    indirect_specular = Inputs.file(
        description='An Radiance .ill file containing indirect irradiance for the '
        'specular version of the aperture group.',
        path='indirect_spec.ill', extensions=['ill', 'irr']
    )

    ref_specular = Inputs.file(
        description='A Radiance .ill containing ground-reflected irradiance for the '
        'specular version of the aperture group.',
        path='ref_spec.ill', extensions=['ill', 'irr']
    )

    indirect_diffuse = Inputs.file(
        description='An Radiance .ill file containing indirect irradiance for the '
        'diffuse version of the aperture group.',
        path='indirect_diff.ill', extensions=['ill', 'irr']
    )

    ref_diffuse = Inputs.file(
        description='A Radiance .ill containing ground-reflected irradiance for the '
        'diffuse version of the aperture group.',
        path='ref_diff.ill', extensions=['ill', 'irr']
    )

    sun_up_hours = Inputs.file(
        description='A sun-up-hours.txt file output by Radiance and aligns with the '
        'input irradiance files.', path='sun-up-hours.txt'
    )

    aperture_id = Inputs.str(
        description='Text string for the identifier of the aperture associated '
        'with the irradiance.'
    )

    @command
    def run_irradiance_contrib(self):
        return 'ladybug-comfort map irradiance-contrib result.sql direct_spec.ill ' \
            'indirect_spec.ill ref_spec.ill indirect_diff.ill ref_diff.ill ' \
            'sun-up-hours.txt --aperture-id "{{self.aperture_id}}" --folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output .ill files.', path='output'
    )


@dataclass
class ShortwaveMrtMap(Function):
    """Get CSV files with maps of shortwave MRT Deltas from Radiance results."""

    epw = Inputs.file(
        description='Weather file used to compute sun positions.',
        path='weather.epw', extensions=['epw']
    )

    indirect_irradiance = Inputs.file(
        description='A Radiance .ill containing the indirect irradiance for each '
        'sensor. Alternatively, if the indirect-is-total input is used, then this '
        'input should be the total irradiance for each sensor.',
        path='indirect.ill', extensions=['ill', 'irr']
    )

    direct_irradiance = Inputs.file(
        description='A Radiance .ill containing direct irradiance for each sensor.',
        path='direct.ill', extensions=['ill', 'irr']
    )

    ref_irradiance = Inputs.file(
        description='A Radiance .ill containing ground-reflected irradiance for each '
        'sensor.', path='ref.ill', extensions=['ill', 'irr']
    )

    sun_up_hours = Inputs.file(
        description='A sun-up-hours.txt file output by Radiance and aligns with the '
        'input irradiance files.', path='sun-up-hours.txt'
    )

    contributions = Inputs.folder(
        description='An optional folder containing sub-folders of irradiance '
        'contributions from dynamic aperture groups. There should be one sub-folder '
        'per window groups and each one should contain three .ill files named '
        'direct.ill, indirect.ill and reflected.ill. If specified, these will be '
        'added to the irradiance inputs before computing shortwave MRT deltas.',
        path='dynamic', optional=True
    )

    solarcal_par = Inputs.str(
        description='A SolarCalParameter string to customize the assumptions of '
        'the SolarCal model.', default='--posture seated --sharp 135 '
        '--absorptivity 0.7 --emissivity 0.95'
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If unspecified, results '
        'will be annual.', default=''
    )

    indirect_is_total = Inputs.str(
        description='A switch to note whether the indirect-irradiance argument is '
        'actually the total irradiance.',
        default='is-indirect',
        spec={'type': 'string', 'enum': ['is-indirect', 'indirect-is-total']}
    )

    @command
    def run_shortwave_map(self):
        return 'ladybug-comfort map shortwave-mrt weather.epw indirect.ill direct.ill ' \
            'ref.ill sun-up-hours.txt --contributions dynamic ' \
            '--solarcal-par "{{self.solarcal_par}}" ' \
            '--run-period "{{self.run_period}}" --{{self.indirect_is_total}} ' \
            '--output-file shortwave.csv'

    shortwave_mrt_map = Outputs.file(
        description='CSV file containing a map of shortwave MRT deltas.',
        path='shortwave.csv'
    )


@dataclass
class LongwaveMrtMap(Function):
    """Get CSV files with maps of longwave MRT from Radiance and EnergyPlus results."""

    result_sql = Inputs.file(
        description='A SQLite file that was generated by EnergyPlus and contains '
        'hourly or sub-hourly thermal comfort results.',
        path='result.sql', extensions=['sql', 'db', 'sqlite']
    )

    view_factors = Inputs.file(
        description='A CSV of spherical view factors to the surfaces in the result-sql.',
        path='view_factors.csv', extensions=['csv']
    )

    modifiers = Inputs.file(
        description='Path to a modifiers file that aligns with the view-factors.',
        path='view_factors.mod', extensions=['mod', 'txt']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    epw = Inputs.file(
        description='Weather file used to estimate conditions for any outdoor '
        'sensors.', path='weather.epw', extensions=['epw']
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If unspecified, results '
        'will be annual.', default=''
    )

    @command
    def run_longwave_map(self):
        return 'ladybug-comfort map longwave-mrt result.sql view_factors.csv ' \
            'view_factors.mod enclosure_info.json weather.epw ' \
            '--run-period "{{self.run_period}}" --output-file longwave.csv'

    longwave_mrt_map = Outputs.file(
        description='CSV file containing a map of longwave MRT.',
        path='longwave.csv'
    )


@dataclass
class AirMap(Function):
    """Get CSV files with maps of air temperatures or humidity from EnergyPlus results.
    """

    result_sql = Inputs.file(
        description='A SQLite file that was generated by EnergyPlus and contains '
        'hourly or sub-hourly thermal comfort results.',
        path='result.sql', extensions=['sql', 'db', 'sqlite']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    epw = Inputs.file(
        description='Weather file used to estimate conditions for any outdoor '
        'sensors.', path='weather.epw', extensions=['epw']
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If unspecified, results '
        'will be annual.', default=''
    )

    metric = Inputs.str(
        description='A switch to note whether the the output matrix should be with '
        'relative humidity or air temperature values.',
        default='air-temperature',
        spec={'type': 'string', 'enum': ['air-temperature', 'relative-humidity']}
    )

    @command
    def run_air_map(self):
        return 'ladybug-comfort map air result.sql enclosure_info.json weather.epw ' \
            '--run-period "{{self.run_period}}" --{{self.metric}} ' \
            '--output-file air.csv'

    air_map = Outputs.file(
        description='CSV file containing a map of air temperatures or humidity.',
        path='air.csv'
    )


@dataclass
class MapResultInfo(Function):
    """Get a JSON that specifies the data type and units for comfort map outputs."""

    comfort_model = Inputs.str(
        description='Text for the comfort model of the thermal mapping '
        'simulation. Choose from: pmv, adaptive, utci.',
        spec={'type': 'string', 'enum': ['pmv', 'adaptive', 'utci']}
    )

    run_period = Inputs.str(
        description='The AnalysisPeriod string that dictates the start and end of '
        'the analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If unspecified, it '
        'will be assumed results are for a full year.', default=''
    )

    qualifier = Inputs.str(
        description='Text for any options used on the comfort map simulation that '
        'change the output data type of results. For example, the write-set-map text '
        'of the pmv map can be passed here to ensure the output of this command is '
        'for SET instead of operative temperature.', default=''
    )

    @command
    def map_results_information(self):
        return 'ladybug-comfort map map-result-info {{self.comfort_model}} ' \
            '--run-period "{{self.run_period}}" --qualifier "{{self.qualifier}}" ' \
            '--folder output --log-file results_info.json'

    results_info_file = Outputs.file(
        description='A JSON that specifies the data type and units for all comfort map '
        'outputs.', path='results_info.json'
    )

    viz_config_file = Outputs.file(
        description='A JSON that specifies configurations for VTK visualizations.',
        path='config.json'
    )

    temperature_info = Outputs.file(
        description='A JSON that specifies the data type and units for temperature map '
        'results.', path='output/temperature.json'
    )

    condition_info = Outputs.file(
        description='A JSON that specifies the data type and units for thermal '
        'condition map results.', path='output/condition.json'
    )

    condition_intensity_info = Outputs.file(
        description='A JSON that specifies the data type and units for '
        'condition intensity map results.', path='output/condition_intensity.json'
    )


@dataclass
class Tcp(Function):
    """Compute Thermal Comfort Petcent (TCP) from thermal condition CSV map."""

    condition_csv = Inputs.file(
        description='A CSV file of thermal conditions output by a thermal mapping '
        'function.', path='condition.csv', extensions=['csv', 'cond']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    occ_schedule_json = Inputs.file(
        description='An occupancy schedule JSON output by the honeybee-energy '
        'model-occ-schedules function.', path='occ_schedule.json',
        extensions=['json']
    )

    schedule = Inputs.file(
        description='An optional path to a CSV file to specify the relevant times '
        'during which comfort should be evaluated. If specified, this will override '
        'the occ-schedule-json for both indoor and outdoor conditions. Values '
        'should be 0-1 separated by new line.',
        path='schedule.txt', optional=True
    )

    @command
    def compute_tcp(self):
        return 'ladybug-comfort map tcp condition.csv enclosure_info.json ' \
            '--schedule schedule.txt --occ-schedule-json occ_schedule.json ' \
            '--folder output'

    tcp = Outputs.file(
        description='A CSV that contains the Thermal Comfort Percent (TCP) for '
        'each sensor.', path='output/tcp.csv'
    )

    hsp = Outputs.file(
        description='A CSV that contains the Heat Sensation Percent (HSP) for '
        'each sensor.', path='output/hsp.csv'
    )

    csp = Outputs.file(
        description='A CSV that contains the Cold Sensation Percent (CSP) for '
        'each sensor.', path='output/csp.csv'
    )
