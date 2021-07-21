import csv
import logging

log = logging.getLogger(__name__)

class CSV_Writer:
    """ This class is responsible for writing the measured times in CSV-files """
    csvfile = None
    writer = None
    preparation = 0
    evaluation = 0
    fieldnames = []

    @classmethod
    def set_prep_time(cls, time):
        """ set time for preparation of the system / adding votes """
        log.debug('Preparation and vote aggregation: {:.3f}s'.format(time))
        cls.preparation = time

    @classmethod
    def set_eval_time(cls, time):
        """ set time for computation of the election result"""
        log.debug('Evaluation time: {:.3f}s'.format(time))
        cls.evaluation = time

    @classmethod
    def init_writer(cls):
        cls.fieldnames = ['Candidates', 'Voter', 'Prep-Time(s)', 'Eval-Time(s)', 'Winners', 'gt-ops', 'eq-ops', 'dec-ops', 'mul-ops', 'System-Name']
        cls.csvfile = open('results/times.csv', 'w', newline='')
        #cls.csvfile2 = open('Dropbox/Ergebnisse/times.csv', 'w', newline='')
        writer = csv.DictWriter(cls.csvfile, fieldnames=cls.fieldnames)
        #writer2 = csv.DictWriter(cls.csvfile2, fieldnames=cls.fieldnames)
        writer.writeheader()
        #writer2.writeheader()
        cls.csvfile.close()
        #cls.csvfile2.close()

    @classmethod
    def write_with_election_params(cls, num_cand, num_voter, system_id, winners=None, gt_operations=None, eq_operations=None, dec_operations=None, mul_operations=None):
        """ write time-relevant parameters and times """
        if len(cls.fieldnames) == 0:
            log.warning("CSV_Writer is not initialized")
            return
        cls.csvfile = open('results/times.csv', 'a', newline='')
        #cls.csvfile2 = open('Dropbox/Ergebnisse/times.csv', 'a', newline='')
        writer = csv.DictWriter(cls.csvfile, fieldnames=cls.fieldnames)
        #writer2 = csv.DictWriter(cls.csvfile2, fieldnames=cls.fieldnames)
        prep = '%.2f'%(cls.preparation)
        eval = '%.2f'%(cls.evaluation)

        writer.writerow({cls.fieldnames[0]: num_cand,
                        cls.fieldnames[1]: num_voter,
                        cls.fieldnames[2]: prep,
                        cls.fieldnames[3]: eval,
                        cls.fieldnames[4]: winners,
                        cls.fieldnames[5]: gt_operations,
                        cls.fieldnames[6]: eq_operations,
                        cls.fieldnames[7]: dec_operations,
                        cls.fieldnames[8]: mul_operations,
                        cls.fieldnames[9]: system_id})
        #writer2.writerow({cls.fieldnames[0]: system_id, cls.fieldnames[1]: num_cand,
        #                 cls.fieldnames[2]: num_voter,
        #                 cls.fieldnames[3]: prep, cls.fieldnames[4]: eval})
        cls.csvfile.close()
        #cls.csvfile2.close()

        log.debug("Succesfully written preparation/aggregation time: " + str(prep))
        log.debug("Succesfully written evaluation time: " + str(eval))

    @classmethod
    def write_error(cls, info, comment):
        """ write the exception info if an exception occured """
        if len(cls.fieldnames) == 0:
            log.warning("CSV_Writer is not initialized")
            return
        cls.csvfile = open('results/times.csv', 'a', newline='')
        #cls.csvfile2 = open('Dropbox/Ergebnisse/times.csv', 'a', newline='')
        writer = csv.DictWriter(cls.csvfile, fieldnames=cls.fieldnames)
        #writer2 = csv.DictWriter(cls.csvfile2, fieldnames=cls.fieldnames)

        writer.writerow({cls.fieldnames[0]: info[0], cls.fieldnames[1]: info[1], cls.fieldnames[2]: comment})
        #writer2.writerow({cls.fieldnames[0]: info[0], cls.fieldnames[1]: info[1], cls.fieldnames[2]: comment})
        cls.csvfile.close()
        #cls.csvfile2.close()
