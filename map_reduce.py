from mrjob.job import MRJob

class MRAverageByAge(MRJob):

    def mapper(self, _, line):
        fields = line.split(',')
        if len(fields) == 14:  # Adjust based on the number of fields in your dataset
            age = fields[2]
            try:
                body_temp = float(fields[5])
                pulse_rate = float(fields[6])
                respiration_rate = float(fields[7])
                blood_pressure = float(fields[8])
                blood_oxygen = float(fields[9])
                weight = float(fields[10])
                blood_glucose = float(fields[11])
                yield (age, 'body_temp'), body_temp
                yield (age, 'pulse_rate'), pulse_rate
                yield (age, 'respiration_rate'), respiration_rate
                yield (age, 'blood_pressure'), blood_pressure
                yield (age, 'blood_oxygen'), blood_oxygen
                yield (age, 'weight'), weight
                yield (age, 'blood_glucose'), blood_glucose
            except ValueError:
                pass

    def reducer(self, key, values):
        field = key[1]
        total = sum(values)
        count = len(values)
        average = total / count
        yield (key[0], field), average

    def reducer_avg_by_age(self, age, values):
        results = {}
        for field, average in values:
            results[field] = average
        yield age, results

if __name__ == '__main__':
    MRAverageByAge.run()
