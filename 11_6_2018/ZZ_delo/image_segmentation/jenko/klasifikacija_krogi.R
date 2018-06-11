setwd("C:\\Users\\zanza\\iCloudDrive\\Desktop\\image_segmentation\\jenko")

barve <- read.table("results_real_zdruzeno.csv", header = T, sep = ",")

summary(barve)

# Randomize the order of the data frame
barve <- barve[sample(1:nrow(barve)), ]

## 75% of the sample size
smp_size <- floor(0.75 * nrow(barve))

## set the seed to make your partition reproducible
set.seed(122)
train_ind <- sample(seq_len(nrow(barve)), size = smp_size)

train <- barve[train_ind, ]
test <- barve[-train_ind, ]


library(rpart)
dt <- rpart(barva ~ ., data = barve)

plot(dt)
text(dt, pretty = 0)


observed <- test$barva
observed

# Napovedane vrednosti modela
# Uporabimo funkcijo "predict", ki potrebuje model, testne primere in obliko,
# v kateri naj poda svoje napovedi. Nastavitev "class" pomeni, da nas zanimajo
# samo razredi, v katere je model klasificiral testne primere.

predicted <- predict(dt, test, type = "class")
predicted

# Zgradimo tabelo napacnih klasifikacij
t <- table(observed, predicted)
t

# Elementi na diagonali predstavljajo pravilno klasificirane testne primere...

# Klasifikacijska tocnost modela
sum(diag(t)) / sum(t)


# Lahko napisemo funkcijo za izracun klasifikacijske tocnosti
CA <- function(prave, napovedane)
{
  t <- table(prave, napovedane)

  sum(diag(t)) / sum(t)
}

# Klic funkcije za klasifikacijsko tocnost...
CA(observed, predicted)






# Druga oblika napovedi modela (nastavitev "prob") vraca verjetnosti,
# da posamezni testni primer pripada dolocenemu razredu.

# Napovedane verjetnosti pripadnosti razredom (odgovor dobimo v obliki matrike)
predMat <- predict(dt, barve, type = "prob")
predMat

# Prave verjetnosti pripadnosti razredom
# (dejanski razred ima verjetnost 1.0 ostali pa 0.0)
obsMat <- model.matrix( ~ BARVA-1, barve)
obsMat

# Funkcija za izracun Brierjeve mere
brier.score <- function(observedMatrix, predictedMatrix)
{
  sum((observedMatrix - predictedMatrix) ^ 2) / nrow(predictedMatrix)
}

# Izracunajmo Brierjevo mero za napovedi nasega drevesa
brier.score(obsMat, predMat)





library(CORElearn)
cm.knn <- CoreModel(BARVA ~ ., data = barve, model="knn", kInNN = 5)
predicted <- predict(cm.knn, test, type="class")
CA(observed, predicted)

predMat <- predict(cm.knn, test, type = "probability")
brier.score(obsMat, predMat)

errorest(Class~., data=learn, model = mymodel.coremodel, predict = mypredict.coremodel, target.model="knn")
