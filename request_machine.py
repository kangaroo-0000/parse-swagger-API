import requests
import json

null = None


class Action():
    def __init__(self, machineIDs=[], machineNames=[], toolSetNames=[], MacUtilizations=[], MacExros=[],
                 MacFirstPass=[], MacPerforms=[], MacOees=[], MacTeeps=[
    ], dailyMachineNames=[], shiftNames=[], machingCounts=[],
            okCounts=[], ngCounts=[], reworkOkCounts=[], reworkNgCounts=[]):

        self.machineIDs = machineIDs
        self.machineNames = machineNames
        self.toolSetNames = toolSetNames
        self.MacUtilizations = MacUtilizations
        self.MacExros = MacExros
        self.MacFirstPass = MacFirstPass
        self.MacPerforms = MacPerforms
        self.MacOees = MacOees
        self.MacTeeps = MacTeeps
        self.dailyMachineNames = dailyMachineNames
        self.shiftNames = shiftNames
        self.machingCounts = machingCounts
        self.okCounts = okCounts
        self.ngCounts = ngCounts
        self.reworkOkCounts = reworkOkCounts
        self.reworkNgCounts = reworkNgCounts

    def find_machineIDs(self, URL):

        json2post = {
            "departmentName": null,
            "factoryName": null,
            "groupName": null,
            "machineName": null,
            "manufacturerName": null,
            "mcName": null,
            "modelName": null
        }

        response = requests.post(URL, json=json2post)
        if not response:
            print("Error connecting to server")

        for dict in response.json():
            try:
                self.machineIDs.append(
                    dict.get('machineToolSetDtoList')[0].get('toolSetId'))
            except KeyError or IndexError:
                continue

        return response.json()

    def find_machine_performance_params(self, URL):

        for ID in self.machineIDs:
            json2post = {
                "loadingTimeId": "WorkTime",
                "shiftIdList": [],
                "startDateFrom": "2022-06-22",
                "startDateTo": "2022-06-23",
                "toolSetIdList": [
                    ID
                ],
                "utilizationTimeId": "MachineTime"
            }
            response = requests.post(URL, json=json2post)
            if not response:
                print("Error connecting to server")

            for dict in response.json():
                for key in dict.keys():
                    if key == "machineName":
                        self.machineNames.append(dict.get('machineName'))
                    if key == "toolSetName":
                        self.toolSetNames.append(dict.get('toolSetName'))
                    if key == "totalMacUtilizationRate":
                        self.MacUtilizations.append(
                            dict.get('totalMacUtilizationRate'))
                    if key == "totalMacExroRate":
                        self.MacExros.append(dict.get('totalMacExroRate'))
                    if key == "totalMacFirstPassYieldRate":
                        self.MacFirstPass.append(
                            dict.get('totalMacFirstPassYieldRate'))
                    if key == "totalMacPerformanceRate":
                        self.MacPerforms.append(
                            dict.get('totalMacPerformaceRate'))
                    if key == "totalMacOee":
                        self.MacOees.append(dict.get('totalMacOee'))
                    if key == "totalMacTeep":
                        self.MacTeeps.append(dict.get('totalMacTeep'))

        return response.json()

    def find_daily_performance_by_ID(self, URL):
        response = requests.get(URL)
        data = response.json()

        self.dailyMachineNames.append(
            data.get('machineToolSetDto').get('machineDto').get('machineName'))
        try:
            self.shiftNames.append(
                data['machineShiftProcessInfoDtoList'][0]['shiftName'])
            self.machingCounts.append(
                data['machineShiftProcessInfoDtoList'][0]['macMachiningCount'])
            self.okCounts.append(
                data['machineShiftProcessInfoDtoList'][0]['totalFirstOkCount'])
            self.ngCounts.append(
                data['machineShiftProcessInfoDtoList'][0]['totalFirstNgCount'])
            self.reworkOkCounts.append(
                data['machineShiftProcessInfoDtoList'][0]['totalReworkOkCount'])
            self.reworkNgCounts.append(
                data['machineShiftProcessInfoDtoList'][0]['totalReworkNgCount'])
        except IndexError:
            return data

        return data

    def calculate_defects_after_rework(self):
        for index, (i, j) in enumerate(zip(self.okCounts, self.ngCounts)):
            try:
                print(
                    f'{self.dailyMachineNames[index]} has a Defect Rate of: {(i-j)/i}')
            except ZeroDivisionError:
                continue

    def calculate_defect_frees_after_rework(self):
        for index, (i, j, k, m) in zip(self.okCounts, self.ngCounts, self.reworkOkCounts, self.reworkNgCounts):
            try:
                print(
                    f'{self.dailyMachineNames[index]} has a Defect Free Rate of: {(i-j+k-m)/i}')
            except ZeroDivisionError:
                continue


def main():
    a = Action()
    data1 = a.find_machineIDs(
        "http://172.16.1.102:8080/machine/getProcessingMachineByFlexibleSearch")
    data2 = a.find_machine_performance_params(
        "http://172.16.1.102:8086/machinePerformace/getMachinePerformaceList")
    for index, ID in enumerate(a.machineIDs):
        data3 = a.find_daily_performance_by_ID(
            f"http://172.16.1.102:8086/machinePerformace/getMachineProcessInfoByShiftAndToolSet/{ID}/2022-06-21")
        if index == 0:  # 如果是第一次開檔案，overwrite原本的
            with open("machineDailyResponse.json", 'w', encoding='utf-8') as f:
                json.dump(data3, f, ensure_ascii=False)
        else:
            with open("machineDailyResponse.json", 'a', encoding='utf-8') as f:
                json.dump(data3, f, ensure_ascii=False)
    with open("machineIDRepsonse.json", 'w', encoding='utf-8') as f1:
        json.dump(data1, f1, ensure_ascii=False)
    with open("machinePerformanceResponse.json", 'w', encoding='utf-8') as f2:
        json.dump(data2, f2, ensure_ascii=False)
    for key in a.__dict__:
        with open(str(key)+".json", 'w', encoding='utf-8') as f:
            json.dump(a.__dict__.get(key),
                      f, ensure_ascii=False)


if __name__ == "__main__":
    main()
