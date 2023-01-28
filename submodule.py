from libcombine import *
import json
import pandas as pd


class importer:
    def __init__(self, path):
        self.path = path
        # self.paths =["2022-10-2Metaraminol production using cv20205_4mL(noEnzymeML).omex","2022-9-1Metaraminol production using cv20205_20mL_1(noEnzymeML).omex"]
        self.paths = [
            "data/2022-10-60mmolLABTS (noEnzymeML).omex",
            "data/2022-10-625mmolLABTS (noEnzymeML).omex",
        ]

    def build_data_frame(self):
        """
        Central method of the data extraction method. It initiates the reading in of enzymeML documenty, extraction
        of the BioCatHub data model and building dataframes, containing the measurement data of the individual enzymeML documents

        Parameters
        ----------
        paths: List
            List containing the paths of the EnzymeML documents to be read in.

        Returns
        -------
        df: DataFrame
            Dataframe containing the measurement data of the selected EnzymeML documents
        """

        data_frame_dict = {}


        bch_model = self.import_enzymeml(self.path)
        if self.check_x_values(data_frame_dict):
            pass
        elif self.check_x_values(data_frame_dict) == False:
            x_values = self.extract_x_values(bch_model)
            data_frame_dict["x_values"] = x_values
        measurements = self.measurement_data_to_df(bch_model)
        #print("measurements", measurements)
        data_frame_dict.update(measurements)

        df = pd.DataFrame(data_frame_dict)
        return df

    def check_x_values(self, data_frame_dict):

        """
        Checks if the submitted dictionary contains the key x_values. Since multiple EnzymeML documents are processed and every
        EnzymeML document contains x_valus, it needs to be checked, if these are already added to the dictionary

        Parameters
        ----------
        data_frame_dict: Dictionary
            Dictionary containing the x and y values of the uploaded EnzyneML documents

        Returns
        -------
        Boolean


        """

        if "x_values" in data_frame_dict.keys():
            return True
        else:
            return False

    def extract_x_values(self, bch_model):

        """
        Extracts and returns the x_values of the submitted BioCatHub data mode.

        Parameters
        ----------
        bch_model: Dict
            BioCatHub data model

        Returns
        -------
        x_values: List
            List containing the x_values of the BioCatHub data model
        """

        measurement_data = bch_model["experimentalData"]["measurements"]

        for i in measurement_data:
            replicate_x = i["replicates"]
            x_values = []
            for j in replicate_x:
                x = j["x_value"]
                x_values.append(x)
        return x_values

    def import_enzymeml(self, path):
        """
        Imports EnzymeML document and extracts the BioCatHub data model

        Parameters
        ----------
        path: String
            Path at which the EnzymeML document is stored

        Returns
        -------
        bch_model: Dict
            Dictionary of the BioCatHub data model
        """

        bch_model = None

        payload = {}

        archive = CombineArchive()
        archive.initializeFromArchive(path)
        experiment = False
        for i in range(archive.getNumEntries()):
            entry = archive.getEntry(i)
            if entry.getLocation() == "biocathub.json":  # TODO #8
                #print(entry.getLocation())
                archive.extractEntry(entry.getLocation(), "biocathub.json")
                with open("biocathub.json") as extract:
                    experiment = json.load(extract)
                    bch_model = experiment
                break
            else:
                pass
        return bch_model

    def measurement_data_to_df(self, bch_model):
        """
        Extracts the y_values from the BioCatHub data model

        Parameters
        ----------
        bch_model: Dict
            BioCatHub data model

        Returns
        -------
        y_values: Dict
            Dictionary containing the y_values of the BioCatHub data model
        """
        measurement_data = bch_model["experimentalData"]["measurements"]
        number_of_replicates = len(measurement_data[0]["replicates"][0]["y_values"])
        number_of_measurements = len(measurement_data[0]["replicates"])
        #print(len(measurement_data))

        y_values = {}


        for i in measurement_data:
            length_of_replicates = len(i["replicates"][0]["y_values"])
            y_container = []
            for x in range(length_of_replicates):
                y_container.append([])

            replicates = i["replicates"]
            for j in replicates:
                replicate = j
                for k in range(number_of_replicates):
                    y_replicates = replicate["y_values"]
                    y_container[k].append(y_replicates[k])
            #reagent_name = i["reagent"]
            reagent_name = "pac"
            #measurement_note = i["notes"]
            #print(i)

            count = measurement_data.index(i)
            #print("COUNT",count)



            for n in range(number_of_replicates):
                y_values["y_values_"+str(count)] = y_container[n]

        return y_values


document1 = importer('data/2022-10-3Hotzymes-BmTA activity assay H2a(noEnzymeML).omex').build_data_frame()