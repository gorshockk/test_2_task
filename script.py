import pandas as pd


class BrandAnalysis:
    def __init__(self, df):
        # Инициализируем данные
        self.data = self.df_preparation(df)

    def df_preparation(self, df):
        # Подготовка данных
        if df.isnull().sum().sum() != 0:
            data = df.dropna(how='any')
        else:
            data = df.copy()
        data['date'] = pd.to_datetime(data['date'])
        data["day"] = data["date"].dt.day
        data["month"] = data["date"].dt.month
        data["year"] = data["date"].dt.year
        return data

    def choose_brand(self, brand):
        # Фильтрация по бренду
        return self.data[self.data.brand == brand]

    def avg_region(self, df):
        # Средние продажи по регионам
        temp = df.groupby("region").agg({"total_sales": sum, "total_stores_count": sum})
        temp["total_sales"] = temp["total_sales"].apply(lambda x: x / 1_000_000)
        temp["avg_sales"] = temp["total_sales"] / temp["total_stores_count"]
        temp["avg_sales"] = temp["avg_sales"].apply(lambda x: x * 1_000_000)
        temp = temp.rename(columns={"total_sales": "total_sales_mln"})
        return temp.sort_values(ascending=False, by="avg_sales")

    def total_info(self):
        # Суммированная информация
        total= self.data.groupby("brand").agg(
            {"total_sales": sum, "total_items_count": sum, "total_receipts_count": sum, "total_stores_count": sum}
        )
        total = total.reset_index(drop=False)
        total = total.sort_values(ascending=False, by="total_sales")
        total = total.reset_index(drop=True)
        return total


    def competitors(self, total, brand):
        # Поиск конкурентов
        res = pd.DataFrame()
        index = total[total["brand"]==brand].index[0]
        if (index >= 2) and (index < len(total) - 2):
            res = total.iloc[max(0, index - 2): index + 3, 0]
        else:
            if index == 1:
                res = total.iloc[0: index + 3, 0]
            if index == 0:
                res = total.iloc[0: index + 4, 0]
            if index == len(total) - 1:
                res = total.iloc[len(total) - 4: len(total) - 1, 0]
            if index == len(total) - 2:
                res = total.iloc[len(total) - 4: len(total) - 1, 0]
        return res[res != brand]

    def compare(self, df_1, df_2):
        # Разница между брендами
        reg_1 = df_1.groupby("region").agg(
            {"total_sales": sum, "total_items_count": sum, "total_receipts_count": sum, "total_stores_count": sum}
        )
        reg_2 = df_2.groupby("region").agg(
            {"total_sales": sum, "total_items_count": sum, "total_receipts_count": sum, "total_stores_count": sum}
        )
        reg_1 = reg_1.reindex(reg_2.index)
        res = reg_1 - reg_2
        return res.sort_values(ascending=False, by="total_sales")

    def difference(self, df):
        # Разница между месяцами
        grouped = df.groupby(["year", "month"]).agg({"total_sales": sum, "total_items_count": sum}).reset_index()
        grouped = grouped.sort_values(by=["year", "month"])
        grouped["sum_difference"] = grouped["total_sales"].diff()
        grouped["items_difference"] = grouped["total_items_count"].diff()
        return grouped.sort_values(ascending=False,by=["total_sales","total_items_count"]).reset_index(drop=True)

    def generate_report(self, brand):
        # Генерация отчёта
        brand_df = self.choose_brand(brand)
        avg_reg = self.avg_region(brand_df)
        total = self.total_info()
        comps = self.competitors(total, brand)
        competitor = self.choose_brand(comps.iloc[0])  # Первый конкурент
        brand_dif = self.difference(competitor)
        compare_df = self.compare(brand_df, competitor)
        return brand_df,avg_reg,total,comps,competitor,brand_dif,compare_df


##############################################

df=pd.read_csv("test_brand_data.csv")
s=input("Введите название компании: ")
analysis = BrandAnalysis(df)

# Генерируем отчёт для бренда "Фрингель"
brand_df,avg_region, total_info,competitors,comp_df, brand_difference, compare_difference = analysis.generate_report(s)

print(f"Средние продажи одного магазина составляют:{round(avg_region["avg_sales"].mean(),2)}.")
print(f"Наиболее количество продаж на один магазин было совершено в {avg_region.index[0]} : {round(avg_region.loc[avg_region.index[0],"avg_sales"],2)} "
      f",самое наименьшее в {avg_region.index[-1]} : {round(avg_region.loc[avg_region.index[-1],"avg_sales"],2)}")
print(f"Список конкурентов:{', '.join(map(str, competitors.tolist()))}.Среди которых самое наибольшее количество продаж совершил: {competitors.iloc[0]}")
print(f"Если сравнивать {s} с {competitors.iloc[0]},то наибольшая отрицательная разница для {s} по продажам "
      f"составляет {round(compare_difference.loc[compare_difference.index[-1],"total_sales"],2)} в  {compare_difference.index[-1]}."
      f"А наибольшая положительная составляет {round(compare_difference.loc[compare_difference.index[0],"total_sales"],2)} в  {compare_difference.index[0]}")
print(f"Если сравнивать действия конкурента,например {competitors[0]}, то {brand_difference.iloc[0,1]}го месяца "
      f"{brand_difference.iloc[0,0]}го года сделал наибольшую закупку товаров в {brand_difference.iloc[0,3]} и ,как следствие, наибольшие продажи в {round(brand_difference.iloc[0,2],2)}")