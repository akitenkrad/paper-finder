from enum import Enum
from collections import namedtuple

ArCat = namedtuple('ArCat', ('name', 'description'))

class ArXivCategory(Enum):
    '''arXiv Taxonomy (https://arxiv.org/category_taxonomy)'''
    CS_ALL = ArCat('cs*', 'CS ALL')
    CS_AI = ArCat('cs.AI', 'Artificial Intelligence')
    CS_AR = ArCat('cs.AR', 'Hardware Architecture')
    CS_CC = ArCat('cs.CC', 'Computational Complexity')
    CS_CE = ArCat('cs.CE', 'Computational Engineering, Finance, and Science')
    CS_CG = ArCat('cs.CG', 'Computational Geometry')
    CS_CL = ArCat('cs.CL', 'Computation and Language')
    CS_CR = ArCat('cs.CR', 'Cryptography and Security')
    CS_CV = ArCat('cs.CV', 'Computer Vision and Pattern Recognition')
    CS_CY = ArCat('cs.CY', 'Computers and Society')
    CS_DB = ArCat('cs.DB', 'Databases')
    CS_DC = ArCat('cs.DC', 'Distributed, Parallel, and Cluster Computing')
    CS_DL = ArCat('cs.DL', 'Digital Libraries')
    CS_DM = ArCat('cs.DM', 'Discrete Mathematics')
    CS_DS = ArCat('cs.DS', 'Data Structures and Algorithms')
    CS_ET = ArCat('cs.ET', 'Emerging Technologies')
    CS_FL = ArCat('cs.FL', 'Formal Languages and Automata Theory')
    CS_GL = ArCat('cs.GL', 'General Literature')
    CS_GR = ArCat('cs.GR', 'Graphics')
    CS_GT = ArCat('cs.GT', 'Computer Science and Game Theory')
    CS_HC = ArCat('cs.HC', 'Human-Computer Interaction')
    CS_IR = ArCat('cs.IR', 'Information Retrieval')
    CS_IT = ArCat('cs.IT', 'Information Theory')
    CS_LG = ArCat('cs.LG', 'Machine Learning')
    CS_LO = ArCat('cs.LO', 'Logic in Computer Science')
    CS_MA = ArCat('cs.MA', 'Multiagent Systems')
    CS_MM = ArCat('cs.MM', 'Multimedia')
    CS_MS = ArCat('cs.MS', 'Mathematical Software')
    CS_NA = ArCat('cs.NA', 'Numerical Analysis')
    CS_NE = ArCat('cs.NE', 'Neural and Evolutionary Computing')
    CS_NI = ArCat('cs.NI', 'Networking and Internet Architecture')
    CS_OH = ArCat('cs.OH', 'Other Computer Science')
    CS_OS = ArCat('cs.OS', 'Operating Systems')
    CS_PF = ArCat('cs.PF', 'Performance')
    CS_PL = ArCat('cs.PL', 'Programming Languages')
    CS_RO = ArCat('cs.RO', 'Robotics')
    CS_SC = ArCat('cs.SC', 'Symbolic Computation')
    CS_SD = ArCat('cs.SD', 'Sound')
    CS_SE = ArCat('cs.SE', 'Software Engineering')
    CS_SI = ArCat('cs.SI', 'Social and Information Networks')
    CS_SY = ArCat('cs.SY', 'Systems and Control')

    ECON_ALL = ArCat('econ.*', 'ECON ALL')
    ECON_EM = ArCat('econ.EM', 'Econometrics')
    ECON_GN = ArCat('econ.GN', 'General Economics')
    ECON_TH = ArCat('econ.TH', 'Theoretical Economics')

    EESS_ALL = ArCat('eess.*', 'EESS ALL')
    EESS_AS = ArCat('eess.AS', 'Audio and Speech Processing')
    EESS_IV = ArCat('eess.IV', 'Image and Video Processing')
    EESS_SP = ArCat('eess.SP', 'Signal Processing')
    EESS_SY = ArCat('eess.SY', 'Systems and Control')

    MATH_ALL = ArCat('math.*', 'MATH ALL')
    MATH_AC = ArCat('math.AC', 'Commutative Algebra')
    MATH_AG = ArCat('math.AG', 'Algebraic Geometry')
    MATH_AP = ArCat('math.AP', 'Analysis of PDEs')
    MATH_AT = ArCat('math.AT', 'Algebraic Topology')
    MATH_CA = ArCat('math.CA', 'Classical Analysis and ODEs')
    MATH_CO = ArCat('math.CO', 'Combinatorics')
    MATH_CT = ArCat('math.CT', 'Category Theory')
    MATH_CV = ArCat('math.CV', 'Complex Variables')
    MATH_DG = ArCat('math.DG', 'Differential Geometry')
    MATH_DS = ArCat('math.DS', 'Dynamical Systems')
    MATH_FA = ArCat('math.FA', 'Functional Analysis')
    MATH_GM = ArCat('math.GM', 'General Mathematics')
    MATH_GN = ArCat('math.GN', 'General Topology')
    MATH_GR = ArCat('math.GR', 'Group Theory')
    MATH_GT = ArCat('math.GT', 'Geometric Topology')
    MATH_HO = ArCat('math.HO', 'History and Overview')
    MATH_IT = ArCat('math.IT', 'Information Theory')
    MATH_KT = ArCat('math.KT', 'K-Theory and Homology')
    MATH_LO = ArCat('math.LO', 'Logic')
    MATH_MG = ArCat('math.MG', 'Metric Geometry')
    MATH_MP = ArCat('math.MP', 'Mathematical Physics')
    MATH_NA = ArCat('math.NA', 'Numerical Analysis')
    MATH_NT = ArCat('math.NT', 'Number Theory')
    MATH_OA = ArCat('math.OA', 'Operator Algebras')
    MATH_OC = ArCat('math.OC', 'Optimization and Control')
    MATH_PR = ArCat('math.PR', 'Probability')
    MATH_QA = ArCat('math.QA', 'Quantum Algebra')
    MATH_RA = ArCat('math.RA', 'Rings and Algebras')
    MATH_RT = ArCat('math.RT', 'Representation Theory')
    MATH_SG = ArCat('math.SG', 'Symplectic Geometry')
    MATH_SP = ArCat('math.SP', 'Spectral Theory')
    MATH_ST = ArCat('math.ST', 'Statistics Theory')

    ASTROPH_ALL = ArCat('astro-ph.*', 'ASTRO-PH ALL')
    ASTROPH_CO = ArCat('astro-ph.CO', 'Cosmology and Nongalactic Astrophysics')
    ASTROPH_EP = ArCat('astro-ph.EP', 'Earth and Planetary Astrophysics')
    ASTROPH_GA = ArCat('astro-ph.GA', 'Astrophysics of Calaxies')
    ASTROPH_HE = ArCat('astro-ph.HE', 'High Energy Astrophysical Phenomena')
    ASTROPH_IM = ArCat('astro-ph.IM', 'Instrumentation and Methods for Astrophysics')
    ASTROPH_SR = ArCat('astro-ph.SR', 'Solar and Stellar Astrophysics')

    CONDMAT_ALL = ArCat('cond-mat.*', 'COND-MAT ALL')
    CONDMAT_DISNN = ArCat('cond-mat.dis-nn', 'Disordered Systems and Neural Networks')
    CONDMAT_MESHALL = ArCat('cond-mat.mes-hall', 'Mesoscale and Nanoscale Physics')
    CONDMAT_MTRLSCI = ArCat('cond-mat.mtrl-sci', 'Materials Science')
    CONDMAT_OTHER = ArCat('cond-mat.other', 'Other Condensed Matter')
    CONDMAT_QUANTGAS = ArCat('cond-mat.quant-gas', 'Auantum Gases')
    CONDMAT_SOFT = ArCat('cond-mat.soft', 'Soft Condensed Matter')
    CONDMAT_STATMECH = ArCat('cond-mat.stat-mech', 'Statistical Mechanics')
    CONDMAT_STREL = ArCat('cond-mat.str-el', 'Strongly Correlated Electrons')
    CONDMAT_SUPRCON = ArCat('cond-mat.supr-con', 'Superconductivity')

    GRQC = ArCat('gr-qc', 'General Relativity and Quantum Cosmology')
    HEPEX = ArCat('hep-ex', 'High Energy Physics - Experiment')
    HEPLAT = ArCat('hep-lat', 'High Energy Physics - Lattice')
    HEPPH = ArCat('hep-ph', 'High Energy Physics - Phenomenology')
    HEPTH = ArCat('hep-th', 'High Energy Physics - Theory')
    MATHPH = ArCat('math-ph', 'Mathematical Physics')

    NLIN_ALL = ArCat('nlin.*', 'NLIN ALL')
    NLIN_AO = ArCat('nlin.AO', 'Adaptation and Self-Organizing Systems')
    NLIN_CD = ArCat('nlin.CD', 'Chaotic Dynamics')
    NLIN_CG = ArCat('nlin.CG', 'Cellular Automata and Lattice Gases')
    NLIN_PS = ArCat('nlin.PS', 'Pattern Formation and Solitons')
    NLIN_SI = ArCat('nlin.SI', 'Exactly Solvable and Integrable Systems')

    NUCLEX = ArCat('nucl-ex', 'Nuclear Experiment')
    NUCLTH = ArCat('nucl-th', 'Nuclear Theory')

    PHYSICS_ALL = ArCat('physics.*', 'PHYSICS ALL')
    PHYSICS_ACCPH = ArCat('physics.acc-ph', 'Accelerator Physics')
    PHYSICS_AOPH = ArCat('physics.ao-ph', 'Atmospheric and Oceanic Physics')
    PHYSICS_APPPH = ArCat('physics.app-ph', 'Applied Physics')
    PHYSICS_ATMCLUS = ArCat('physics.atm-clus', 'Atomic and Molecular Clusters')
    PHYSICS_ATOMPH = ArCat('physics.atom-ph', 'Atomic Physics')
    PHYSICS_BIOPH = ArCat('physics.bio-ph', 'Biological Physics')
    PHYSICS_CLASSPH = ArCat('physics.class-ph', 'Classical Physics')
    PHYSICS_COMPPH = ArCat('physics.comp-ph', 'Computational Physics')
    PHYSICS_DATAAN = ArCat('physics.data-an', 'Data Analysis, Statistics and Probability')
    PHYSICS_EDPH = ArCat('physics.ed-ph', 'Physics Education')
    PHYSICS_FLUDYN = ArCat('physics.flu-dyn', 'Fluid Dynamics')
    PHYSICS_GENPH = ArCat('physics.gen-ph', 'General Physics')
    PHYSICS_GEOPH = ArCat('physics.geo-ph', 'Geophysics')
    PHYSICS_HISTPH = ArCat('physics.hist-ph', 'History and Philosophy of Physics')
    PHYSICS_INSDET = ArCat('physics.ins-det', 'Instrumentation and Detectors')
    PHYSICS_MEDPH = ArCat('physics.med-ph', 'Medical Physics')
    PHYSICS_OPTICS = ArCat('physics.optics', 'Optics')
    PHYSICS_PLASMPH = ArCat('physics.plasm-ph', 'Plasma Physics')
    PHYSICS_POPPH = ArCat('physics.pop-ph', 'Popular Physics')
    PHYSICS_SOCPH = ArCat('physics.soc-ph', 'Physics and Society')
    PHYSICS_SPACEPH = ArCat('physics.space-ph', 'Space Physics')

    QUANTPH = ArCat('quant-ph', 'Quantum Physics')

    QBIO_ALL = ArCat('q-bio.*', 'Q-BIO ALL')
    QBIO_BM = ArCat('q-bio.BM', 'Biomolecules')
    QBIO_CB = ArCat('q-bio.CB', 'Cell Behavior')
    QBIO_GN = ArCat('q-bio.GN', 'Genomics')
    QBIO_MN = ArCat('q-bio.MN', 'Molecular Networks')
    QBIO_NC = ArCat('q-bio.NC', 'Neurons and Cognition')
    QBIO_OT = ArCat('q-bio.OT', 'Other Quantitative Biology')
    QBIO_PE = ArCat('q-bio.PE', 'Populations and Evolution')
    QBIO_QM = ArCat('q-bio.QM', 'Quantitative Methods')
    QBIO_SC = ArCat('q-bio.SC', 'Subcellular Processes')
    QBIO_TO = ArCat('q-bio.TO', 'Tissues and Organs')

    QFIN_ALL = ArCat('q-fin.*', 'Q-FIN ALL')
    QFIN_CP = ArCat('q-fin.CP', 'Computational Finance')
    QFIN_EC = ArCat('q-fin.EC', 'Economics')
    QFIN_GN = ArCat('q-fin.GN', 'General Finance')
    QFIN_MF = ArCat('q-fin.MF', 'Mathematical Finance')
    QFIN_PM = ArCat('q-fin.PM', 'Portfolio Management')
    QFIN_PR = ArCat('q-fin.PR', 'Pricing of Securities')
    QFIN_RM = ArCat('q-fin.RM', 'Risk Management')
    QFIN_ST = ArCat('q-fin.ST', 'Statistical Finance')
    QFIN_TR = ArCat('q-fin.TR', 'Trading and Market Microstructure')

    STAT_ALL = ArCat('stat.*', 'STAT ALL')
    STAT_AP = ArCat('stat.AP', 'Applications')
    STAT_CO = ArCat('stat.CO', 'Computation')
    STAT_ME = ArCat('stat.ME', 'Methodology')
    STAT_ML = ArCat('stat.ML', 'Machine Learning')
    STAT_OT = ArCat('stat.OT', 'Other Statistics')
    STAT_TH = ArCat('stat.TH', 'Statisticas Theory')
